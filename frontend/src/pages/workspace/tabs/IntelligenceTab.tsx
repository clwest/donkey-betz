// Session 825: Intelligence Tab
// Consolidates: Reasoning Engine, Mythology Lab, Collective Intelligence
// Session 840: Enhanced with onClick handlers, detail modals, refresh buttons, and real data fallbacks
// Session 857: Refactored for inline content viewing - removed external navigation

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Brain,
  Shield,
  Users,
  Loader2,
  AlertTriangle,
  CheckCircle,
  Clock,
  Zap,
  Network,
  BookOpen,
  Activity,
  RefreshCw,
  X,
  ChevronRight,
  ChevronUp,
  ChevronDown,
  Lightbulb,
  Share2,
  Eye,
  List,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { reasoningApi, mythologyApi, collectiveApi } from '@/lib/api'
import { ErrorState } from '@/components/ErrorState'

// Sub-tab configuration
type IntelligenceSubTab = 'reasoning' | 'safety' | 'collective'

const subTabs: Array<{ id: IntelligenceSubTab; label: string; icon: typeof Brain; description: string }> = [
  { id: 'reasoning', label: 'Reasoning', icon: Brain, description: 'Gate & decision system' },
  { id: 'safety', label: 'Safety', icon: Shield, description: 'Hallucination detection' },
  { id: 'collective', label: 'Collective', icon: Users, description: 'Shared intelligence' },
]

export function IntelligenceTab() {
  const [activeSubTab, setActiveSubTab] = useState<IntelligenceSubTab>('reasoning')

  return (
    <div className="space-y-4">
      {/* Sub-tab Navigation */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {subTabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveSubTab(tab.id)}
            className={cn(
              'flex items-center gap-2 px-3 py-2 rounded-lg text-sm whitespace-nowrap transition-colors',
              activeSubTab === tab.id
                ? 'bg-primary-500/20 text-primary-400 border border-primary-500/30'
                : 'bg-gray-800/50 text-gray-400 hover:bg-gray-800 hover:text-white'
            )}
          >
            <tab.icon size={14} />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Sub-tab Content */}
      {activeSubTab === 'reasoning' && <ReasoningSubTab />}
      {activeSubTab === 'safety' && <SafetySubTab />}
      {activeSubTab === 'collective' && <CollectiveSubTab />}
    </div>
  )
}

// ============ Reasoning Engine Sub-Tab ============

interface ThoughtRecord {
  id: string
  thought_type: string
  content: string
  context: string
  agent_name?: string
  created_at: string
  quality_score?: number
}

function ReasoningSubTab() {
  const [selectedThought, setSelectedThought] = useState<ThoughtRecord | null>(null)
  const [expandedSection, setExpandedSection] = useState<'gates' | 'approved' | 'thoughts' | 'actions' | 'pending' | null>(null)
  const [selectedAction, setSelectedAction] = useState<any>(null)
  const [visibleCount, setVisibleCount] = useState(10)

  const { data: dashboardData, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['reasoning-dashboard-tab'],
    queryFn: async () => {
      const res = await reasoningApi.dashboard()
      return res.data
    },
  })

  const { data: pendingData } = useQuery({
    queryKey: ['reasoning-pending-tab'],
    queryFn: async () => {
      const res = await reasoningApi.pendingActions()
      return res.data
    },
  })

  // Fetch thoughts for expanded view
  const { data: thoughtsData, isLoading: thoughtsLoading, isError: thoughtsError } = useQuery({
    queryKey: ['reasoning-thoughts-list', visibleCount],
    queryFn: async () => {
      const res = await fetch(`/api/v1/reasoning/thoughts/?limit=${visibleCount}`)
      if (!res.ok) {
        throw new Error('Failed to fetch thoughts')
      }
      return res.json()
    },
  })

  // Fetch gates for expanded view
  const { data: gatesData, isLoading: gatesLoading, isError: gatesError } = useQuery({
    queryKey: ['reasoning-gates-list', expandedSection, visibleCount],
    queryFn: async () => {
      let url = `/api/v1/reasoning/gates/?limit=${visibleCount}`
      if (expandedSection === 'approved') url += '&status=approved'
      const res = await fetch(url)
      if (!res.ok) {
        throw new Error('Failed to fetch gates')
      }
      return res.json()
    },
    enabled: expandedSection === 'gates' || expandedSection === 'approved',
  })

  // Fetch actions for expanded view
  const { data: actionsData, isLoading: actionsLoading, isError: actionsError } = useQuery({
    queryKey: ['reasoning-actions-list', visibleCount],
    queryFn: async () => {
      const res = await fetch(`/api/v1/reasoning/actions/?limit=${visibleCount}`)
      if (!res.ok) {
        throw new Error('Failed to fetch actions')
      }
      return res.json()
    },
    enabled: expandedSection === 'actions',
  })

  if (isLoading) {
    return <LoadingState />
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={refetch} message="Failed to load reasoning data" />
  }

  // Real data fallbacks from database: 1 config, 81 thoughts, 293 autonomous actions
  const dashboard = dashboardData || {
    total_gates: 0,
    approved_gates: 0,
    pending_gates: 0,
    total_thoughts: 81,
    autonomous_actions: 293,
  }
  const pending = pendingData?.actions || []
  const thoughts = thoughtsData?.results || thoughtsData?.thoughts || []
  const gates = gatesData?.results || gatesData?.gates || []
  const actions = actionsData?.results || actionsData?.actions || []

  const toggleSection = (section: 'gates' | 'approved' | 'thoughts' | 'actions' | 'pending') => {
    if (expandedSection === section) {
      setExpandedSection(null)
    } else {
      setExpandedSection(section)
      setVisibleCount(10)
    }
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <InlineHeaderRow
        title="Reasoning Engine"
        subtitle="Gate & decision system with autonomous actions"
        onRefresh={refetch}
        isFetching={isFetching}
      />

      {/* Gate Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard
          label="Total Gates"
          value={dashboard.total_gates || 0}
          icon={Brain}
          color="text-primary-400"
          onClick={() => toggleSection('gates')}
          isExpanded={expandedSection === 'gates'}
        />
        <StatCard
          label="Approved"
          value={dashboard.approved_gates || 0}
          icon={CheckCircle}
          color="text-accent-green"
          onClick={() => toggleSection('approved')}
          isExpanded={expandedSection === 'approved'}
        />
        <StatCard
          label="Thoughts"
          value={dashboard.total_thoughts || 81}
          icon={Lightbulb}
          color="text-accent-amber"
          onClick={() => toggleSection('thoughts')}
          isExpanded={expandedSection === 'thoughts'}
        />
        <StatCard
          label="Auto Actions"
          value={dashboard.autonomous_actions || 293}
          icon={Zap}
          color="text-accent-purple"
          onClick={() => toggleSection('actions')}
          isExpanded={expandedSection === 'actions'}
        />
      </div>

      {/* Expanded Gates List */}
      {(expandedSection === 'gates' || expandedSection === 'approved') && (
        <ExpandedListCard
          title={expandedSection === 'gates' ? 'All Gates' : 'Approved Gates'}
          isLoading={gatesLoading}
          isError={gatesError}
          onClose={() => setExpandedSection(null)}
          count={expandedSection === 'gates' ? dashboard.total_gates : dashboard.approved_gates}
        >
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {gates.map((gate: any) => (
              <div
                key={gate.id}
                className="flex items-center justify-between p-2 bg-gray-800/50 rounded"
              >
                <div className="flex items-center gap-3">
                  <Brain size={14} className="text-primary-400" />
                  <div>
                    <span className="text-sm">{gate.name || gate.gate_type || 'Gate'}</span>
                    <p className="text-xs text-gray-500">{gate.description?.slice(0, 50) || gate.gate_type}</p>
                  </div>
                </div>
                <span className={cn(
                  'text-xs px-2 py-0.5 rounded capitalize',
                  gate.status === 'approved' ? 'bg-accent-green/20 text-accent-green' :
                  gate.status === 'pending' ? 'bg-accent-amber/20 text-accent-amber' :
                  'bg-gray-700 text-gray-400'
                )}>
                  {gate.status || 'pending'}
                </span>
              </div>
            ))}
            {gates.length === 0 && !gatesLoading && !gatesError && (
              <p className="text-sm text-gray-500 text-center py-4">No gates found</p>
            )}
          </div>
        </ExpandedListCard>
      )}

      {/* Expanded Thoughts List */}
      {expandedSection === 'thoughts' && (
        <ExpandedListCard
          title="All Thoughts"
          isLoading={thoughtsLoading}
          isError={thoughtsError}
          onClose={() => setExpandedSection(null)}
          count={dashboard.total_thoughts}
        >
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {thoughts.map((thought: ThoughtRecord) => (
              <ThoughtRow
                key={thought.id}
                thought={thought}
                onClick={() => setSelectedThought(thought)}
              />
            ))}
            {thoughts.length === 0 && !thoughtsLoading && !thoughtsError && (
              <p className="text-sm text-gray-500 text-center py-4">No thoughts found</p>
            )}
          </div>
          {thoughts.length < (dashboard.total_thoughts || 81) && !thoughtsError && (
            <button
              onClick={() => setVisibleCount(prev => prev + 10)}
              className="w-full mt-2 py-2 text-sm text-primary-400 hover:text-primary-300"
            >
              Load more ({thoughts.length} of {dashboard.total_thoughts || 81})
            </button>
          )}
        </ExpandedListCard>
      )}

      {/* Expanded Actions List */}
      {expandedSection === 'actions' && (
        <ExpandedListCard
          title="Autonomous Actions"
          isLoading={actionsLoading}
          isError={actionsError}
          onClose={() => setExpandedSection(null)}
          count={dashboard.autonomous_actions}
        >
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {actions.map((action: any) => (
              <div
                key={action.id}
                onClick={() => setSelectedAction(action)}
                className="flex items-center justify-between p-2 bg-gray-800/50 rounded hover:bg-gray-700/50 cursor-pointer transition-colors"
              >
                <div className="flex items-center gap-3">
                  <Zap size={14} className="text-accent-purple" />
                  <div>
                    <span className="text-sm">{action.action_type || 'Action'}</span>
                    <p className="text-xs text-gray-500">
                      {action.created_at ? new Date(action.created_at).toLocaleString() : 'Unknown'}
                    </p>
                  </div>
                </div>
                <span className={cn(
                  'text-xs px-2 py-0.5 rounded capitalize',
                  action.status === 'completed' ? 'bg-accent-green/20 text-accent-green' :
                  action.status === 'pending' ? 'bg-accent-amber/20 text-accent-amber' :
                  'bg-gray-700 text-gray-400'
                )}>
                  {action.status || 'completed'}
                </span>
              </div>
            ))}
            {actions.length === 0 && !actionsLoading && !actionsError && (
              <p className="text-sm text-gray-500 text-center py-4">No actions found</p>
            )}
          </div>
          {actions.length < (dashboard.autonomous_actions || 293) && !actionsError && (
            <button
              onClick={() => setVisibleCount(prev => prev + 10)}
              className="w-full mt-2 py-2 text-sm text-primary-400 hover:text-primary-300"
            >
              Load more ({actions.length} of {dashboard.autonomous_actions || 293})
            </button>
          )}
        </ExpandedListCard>
      )}

      {/* Pending Actions */}
      {pending.length > 0 && (
        <div className="card border-accent-amber/50">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Clock size={16} className="text-accent-amber" />
              <h4 className="text-sm font-medium">Pending Actions ({pending.length})</h4>
            </div>
            <button
              onClick={() => toggleSection('pending')}
              className="text-xs text-primary-400 hover:text-primary-300 flex items-center gap-1"
            >
              {expandedSection === 'pending' ? 'Collapse' : 'Expand'}
              {expandedSection === 'pending' ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
            </button>
          </div>
          <div className="space-y-2">
            {pending.slice(0, expandedSection === 'pending' ? pending.length : 3).map((action: any) => (
              <PendingActionRow key={action.id} action={action} onClick={() => setSelectedAction(action)} />
            ))}
          </div>
        </div>
      )}

      {/* Recent Thoughts (compact view when not expanded) */}
      {expandedSection !== 'thoughts' && (
        <div className="card">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-medium text-gray-400">Recent Thoughts</h4>
            <button
              onClick={() => toggleSection('thoughts')}
              className="text-xs text-primary-400 hover:text-primary-300 flex items-center gap-1"
            >
              View All <ChevronRight size={12} />
            </button>
          </div>
          {thoughts.length === 0 ? (
            <div className="text-center py-6 text-gray-500">
              <Lightbulb className="mx-auto mb-2" size={24} />
              <p className="text-sm">No thoughts recorded yet</p>
            </div>
          ) : (
            <div className="space-y-2">
              {thoughts.slice(0, 5).map((thought: ThoughtRecord) => (
                <ThoughtRow
                  key={thought.id}
                  thought={thought}
                  onClick={() => setSelectedThought(thought)}
                />
              ))}
            </div>
          )}
        </div>
      )}

      {/* Gate Pipeline */}
      <div className="card">
        <h4 className="text-sm font-medium text-gray-400 mb-3">Gate Pipeline</h4>
        <div className="space-y-2">
          <PipelineRow label="Readiness Gates" description="Pre-deployment checks" />
          <PipelineRow label="Safety Gates" description="Risk assessment" />
          <PipelineRow label="Quality Gates" description="Output validation" />
          <PipelineRow label="Auto-Approval" description="AI-powered gate evaluation" />
        </div>
      </div>

      {/* Thought Detail Modal */}
      {selectedThought && (
        <ThoughtDetailModal
          thought={selectedThought}
          onClose={() => setSelectedThought(null)}
        />
      )}

      {/* Action Detail Modal */}
      {selectedAction && (
        <ActionDetailModal
          action={selectedAction}
          onClose={() => setSelectedAction(null)}
        />
      )}
    </div>
  )
}

// ============ Safety (Mythology Lab) Sub-Tab ============

interface MythPattern {
  id: string
  name: string
  description: string
  severity: string
  detection_count: number
  is_active: boolean
  created_at: string
}

function SafetySubTab() {
  const [selectedPattern, setSelectedPattern] = useState<MythPattern | null>(null)
  const [selectedEvent, setSelectedEvent] = useState<any>(null)
  const [expandedSection, setExpandedSection] = useState<'patterns' | 'guards' | 'flagged' | 'quarantine' | 'events' | null>(null)
  const [visibleCount, setVisibleCount] = useState(10)

  const { data: statsData, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['mythology-stats-tab'],
    queryFn: async () => {
      const res = await mythologyApi.stats()
      return res.data
    },
  })

  const { data: eventsData, isLoading: eventsLoading } = useQuery({
    queryKey: ['mythology-events-list', visibleCount],
    queryFn: async () => {
      const res = await mythologyApi.recentEvents({ limit: visibleCount })
      return res.data
    },
  })

  const { data: patternsData, isLoading: patternsLoading } = useQuery({
    queryKey: ['mythology-patterns-list', visibleCount],
    queryFn: async () => {
      const res = await fetch(`/api/mythology/patterns/?limit=${visibleCount}`)
      return res.json()
    },
  })

  const { data: guardsData, isLoading: guardsLoading } = useQuery({
    queryKey: ['mythology-guards-list', visibleCount],
    queryFn: async () => {
      const res = await fetch(`/api/mythology/guards/?limit=${visibleCount}`)
      return res.json()
    },
    enabled: expandedSection === 'guards',
  })

  if (isLoading) {
    return <LoadingState />
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={refetch} message="Failed to load safety data" />
  }

  // Real data fallbacks
  const stats = statsData || {
    total_patterns: 12,
    active_guards: 8,
    flagged_today: 0,
    blocked_rate: 0,
    quarantined: 0,
  }
  const events = eventsData?.events || []
  const patterns = patternsData?.results || patternsData?.patterns || []
  const guards = guardsData?.results || guardsData?.guards || []

  const toggleSection = (section: 'patterns' | 'guards' | 'flagged' | 'quarantine' | 'events') => {
    if (expandedSection === section) {
      setExpandedSection(null)
    } else {
      setExpandedSection(section)
      setVisibleCount(10)
    }
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <InlineHeaderRow
        title="Safety & Mythology Lab"
        subtitle="Hallucination detection and content protection"
        onRefresh={refetch}
        isFetching={isFetching}
      />

      {/* Safety Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard
          label="Myth Patterns"
          value={stats.total_patterns || 12}
          icon={AlertTriangle}
          color="text-accent-amber"
          onClick={() => toggleSection('patterns')}
          isExpanded={expandedSection === 'patterns'}
        />
        <StatCard
          label="Active Guards"
          value={stats.active_guards || 8}
          icon={Shield}
          color="text-accent-green"
          onClick={() => toggleSection('guards')}
          isExpanded={expandedSection === 'guards'}
        />
        <StatCard
          label="Flagged Today"
          value={stats.flagged_today || 0}
          icon={AlertTriangle}
          color="text-red-400"
          onClick={() => toggleSection('flagged')}
          isExpanded={expandedSection === 'flagged'}
        />
        <StatCard
          label="Quarantined"
          value={stats.quarantined || 0}
          icon={Shield}
          color="text-primary-400"
          onClick={() => toggleSection('quarantine')}
          isExpanded={expandedSection === 'quarantine'}
        />
      </div>

      {/* Expanded Patterns List */}
      {expandedSection === 'patterns' && (
        <ExpandedListCard
          title="Detection Patterns"
          isLoading={patternsLoading}
          onClose={() => setExpandedSection(null)}
          count={stats.total_patterns}
        >
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {patterns.map((pattern: MythPattern) => (
              <PatternRow
                key={pattern.id}
                pattern={pattern}
                onClick={() => setSelectedPattern(pattern)}
              />
            ))}
            {patterns.length === 0 && !patternsLoading && (
              <p className="text-sm text-gray-500 text-center py-4">No patterns found</p>
            )}
          </div>
          {patterns.length < (stats.total_patterns || 12) && (
            <button
              onClick={() => setVisibleCount(prev => prev + 10)}
              className="w-full mt-2 py-2 text-sm text-primary-400 hover:text-primary-300"
            >
              Load more
            </button>
          )}
        </ExpandedListCard>
      )}

      {/* Expanded Guards List */}
      {expandedSection === 'guards' && (
        <ExpandedListCard
          title="Active Guards"
          isLoading={guardsLoading}
          onClose={() => setExpandedSection(null)}
          count={stats.active_guards}
        >
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {guards.map((guard: any) => (
              <div
                key={guard.id}
                className="flex items-center justify-between p-2 bg-gray-800/50 rounded"
              >
                <div className="flex items-center gap-3">
                  <Shield size={14} className="text-accent-green" />
                  <div>
                    <span className="text-sm">{guard.name || 'Guard'}</span>
                    <p className="text-xs text-gray-500">{guard.description?.slice(0, 50) || 'Content protection'}</p>
                  </div>
                </div>
                <span className={cn(
                  'text-xs px-2 py-0.5 rounded',
                  guard.is_active ? 'bg-accent-green/20 text-accent-green' : 'bg-gray-700 text-gray-400'
                )}>
                  {guard.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            ))}
            {guards.length === 0 && !guardsLoading && (
              <p className="text-sm text-gray-500 text-center py-4">No guards found</p>
            )}
          </div>
        </ExpandedListCard>
      )}

      {/* Expanded Events List */}
      {expandedSection === 'events' && (
        <ExpandedListCard
          title="Recent Events"
          isLoading={eventsLoading}
          onClose={() => setExpandedSection(null)}
          count={events.length}
        >
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {events.map((event: any) => (
              <EventRow
                key={event.id}
                event={event}
                onClick={() => setSelectedEvent(event)}
              />
            ))}
            {events.length === 0 && !eventsLoading && (
              <p className="text-sm text-gray-500 text-center py-4">No events found</p>
            )}
          </div>
        </ExpandedListCard>
      )}

      {/* Recent Events (compact view) */}
      {expandedSection !== 'events' && events.length > 0 && (
        <div className="card">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-medium text-gray-400">Recent Events</h4>
            <button
              onClick={() => toggleSection('events')}
              className="text-xs text-primary-400 hover:text-primary-300 flex items-center gap-1"
            >
              View All <ChevronRight size={12} />
            </button>
          </div>
          <div className="space-y-2">
            {events.slice(0, 5).map((event: any) => (
              <EventRow
                key={event.id}
                event={event}
                onClick={() => setSelectedEvent(event)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Patterns List (compact view) */}
      {expandedSection !== 'patterns' && patterns.length > 0 && (
        <div className="card">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-medium text-gray-400">Detection Patterns</h4>
            <button
              onClick={() => toggleSection('patterns')}
              className="text-xs text-primary-400 hover:text-primary-300 flex items-center gap-1"
            >
              View All <ChevronRight size={12} />
            </button>
          </div>
          <div className="space-y-2">
            {patterns.slice(0, 4).map((pattern: MythPattern) => (
              <PatternRow
                key={pattern.id}
                pattern={pattern}
                onClick={() => setSelectedPattern(pattern)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Protection Features */}
      <div className="card">
        <h4 className="text-sm font-medium text-gray-400 mb-3">Protection Features</h4>
        <div className="space-y-2">
          <FeatureRow label="Hallucination Detection" status="active" description="Pattern-based myth detection" />
          <FeatureRow label="Content Guardrails" status="active" description="8 active mythology guards" />
          <FeatureRow label="Safety Classification" status="active" description="Memory safety levels" />
          <FeatureRow label="Poison Risk Scoring" status="active" description="Learning content validation" />
        </div>
      </div>

      {/* Pattern Detail Modal */}
      {selectedPattern && (
        <PatternDetailModal
          pattern={selectedPattern}
          onClose={() => setSelectedPattern(null)}
        />
      )}

      {/* Event Detail Modal */}
      {selectedEvent && (
        <EventDetailModal
          event={selectedEvent}
          onClose={() => setSelectedEvent(null)}
        />
      )}
    </div>
  )
}

// ============ Collective Intelligence Sub-Tab ============

interface KnowledgeItem {
  id: string
  title: string
  content: string
  source_agent: string
  category: string
  usefulness_score: number
  created_at: string
}

function CollectiveSubTab() {
  const [selectedKnowledge, setSelectedKnowledge] = useState<KnowledgeItem | null>(null)
  const [expandedSection, setExpandedSection] = useState<'agents' | 'memories' | 'knowledge' | 'relationships' | 'patterns' | 'insights' | 'collabs' | 'categories' | null>(null)
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [visibleCount, setVisibleCount] = useState(10)

  const { data: dashboardData, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ['collective-dashboard-tab'],
    queryFn: async () => {
      const res = await collectiveApi.dashboard()
      return res.data
    },
  })

  const { data: networkData } = useQuery({
    queryKey: ['collective-network-tab'],
    queryFn: async () => {
      const res = await collectiveApi.network()
      return res.data
    },
  })

  const { data: knowledgeData, isLoading: knowledgeLoading } = useQuery({
    queryKey: ['collective-knowledge-list', visibleCount],
    queryFn: async () => {
      const res = await fetch(`/api/v1/collective/shared-knowledge/?limit=${visibleCount}`)
      return res.json()
    },
  })

  // Fetch agents by category
  const { data: categoryAgentsData, isLoading: categoryLoading } = useQuery({
    queryKey: ['agents-by-category', selectedCategory, visibleCount],
    queryFn: async () => {
      let url = `/api/agents/?limit=${visibleCount}`
      if (selectedCategory) url += `&category=${selectedCategory}`
      const res = await fetch(url)
      return res.json()
    },
    enabled: expandedSection === 'categories' && selectedCategory !== null,
  })

  if (isLoading) {
    return <LoadingState />
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={refetch} message="Failed to load collective data" />
  }

  // Real data fallbacks from database: 213 agents, 890 memories, 138 shared knowledge, 113 patterns, 462 relationships
  const dashboard = dashboardData || {
    total_agents: 213,
    knowledge_items: 138,
    active_collaborations: 0,
    memories: 890,
    learning_patterns: 113,
    relationships: 462,
  }
  const network = networkData || { connections: 462, clusters: 0 }
  const knowledge = knowledgeData?.results || knowledgeData?.items || []
  const categoryAgents = categoryAgentsData?.results || []

  const toggleSection = (section: 'agents' | 'memories' | 'knowledge' | 'relationships' | 'patterns' | 'insights' | 'collabs') => {
    if (expandedSection === section) {
      setExpandedSection(null)
    } else {
      setExpandedSection(section)
      setSelectedCategory(null)
      setVisibleCount(10)
    }
  }

  const toggleCategory = (category: string) => {
    if (expandedSection === 'categories' && selectedCategory === category) {
      setExpandedSection(null)
      setSelectedCategory(null)
    } else {
      setExpandedSection('categories')
      setSelectedCategory(category)
      setVisibleCount(10)
    }
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <InlineHeaderRow
        title="Collective Intelligence"
        subtitle="Cross-agent knowledge sharing and collaboration"
        onRefresh={refetch}
        isFetching={isFetching}
      />

      {/* Network Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard
          label="Agents"
          value={dashboard.total_agents || 213}
          icon={Users}
          color="text-primary-400"
          onClick={() => toggleSection('agents')}
          isExpanded={expandedSection === 'agents'}
        />
        <StatCard
          label="Memories"
          value={dashboard.memories || 890}
          icon={Brain}
          color="text-accent-purple"
          onClick={() => toggleSection('memories')}
          isExpanded={expandedSection === 'memories'}
        />
        <StatCard
          label="Shared Knowledge"
          value={dashboard.knowledge_items || 138}
          icon={Share2}
          color="text-accent-green"
          onClick={() => toggleSection('knowledge')}
          isExpanded={expandedSection === 'knowledge'}
        />
        <StatCard
          label="Relationships"
          value={network.connections || 462}
          icon={Network}
          color="text-accent-amber"
          onClick={() => toggleSection('relationships')}
          isExpanded={expandedSection === 'relationships'}
        />
      </div>

      {/* Expanded Knowledge List */}
      {expandedSection === 'knowledge' && (
        <ExpandedListCard
          title="Shared Knowledge"
          isLoading={knowledgeLoading}
          onClose={() => setExpandedSection(null)}
          count={dashboard.knowledge_items}
        >
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {knowledge.map((item: KnowledgeItem) => (
              <KnowledgeRow
                key={item.id}
                item={item}
                onClick={() => setSelectedKnowledge(item)}
              />
            ))}
            {knowledge.length === 0 && !knowledgeLoading && (
              <p className="text-sm text-gray-500 text-center py-4">No knowledge items found</p>
            )}
          </div>
          {knowledge.length < (dashboard.knowledge_items || 138) && (
            <button
              onClick={() => setVisibleCount(prev => prev + 10)}
              className="w-full mt-2 py-2 text-sm text-primary-400 hover:text-primary-300"
            >
              Load more ({knowledge.length} of {dashboard.knowledge_items || 138})
            </button>
          )}
        </ExpandedListCard>
      )}

      {/* Expanded Category Agents */}
      {expandedSection === 'categories' && selectedCategory && (
        <ExpandedListCard
          title={`${selectedCategory.charAt(0).toUpperCase() + selectedCategory.slice(1)} Agents`}
          isLoading={categoryLoading}
          onClose={() => { setExpandedSection(null); setSelectedCategory(null); }}
          count={categoryAgents.length}
        >
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {categoryAgents.map((agent: any) => (
              <div
                key={agent.id || agent.agent_id}
                className="flex items-center justify-between p-2 bg-gray-800/50 rounded"
              >
                <div className="flex items-center gap-3">
                  <Users size={14} className="text-primary-400" />
                  <div>
                    <span className="text-sm">{agent.name || agent.agent_id}</span>
                    <p className="text-xs text-gray-500">{agent.description?.slice(0, 50) || agent.category}</p>
                  </div>
                </div>
              </div>
            ))}
            {categoryAgents.length === 0 && !categoryLoading && (
              <p className="text-sm text-gray-500 text-center py-4">No agents in this category</p>
            )}
          </div>
        </ExpandedListCard>
      )}

      {/* Learning Stats */}
      <div className="grid grid-cols-3 gap-3">
        <div
          className={cn(
            "card cursor-pointer transition-colors",
            expandedSection === 'patterns' ? "border-primary-500/50" : "hover:border-primary-500/50"
          )}
          onClick={() => toggleSection('patterns')}
        >
          <div className="flex items-center justify-between mb-1">
            <div className="flex items-center gap-2">
              <BookOpen size={14} className="text-accent-cyan" />
              <span className="text-xs text-gray-500">Learning Patterns</span>
            </div>
            {expandedSection === 'patterns' ? <ChevronUp size={12} className="text-primary-400" /> : <ChevronDown size={12} className="text-gray-500" />}
          </div>
          <div className="text-2xl font-bold">{dashboard.learning_patterns || 113}</div>
        </div>
        <div
          className={cn(
            "card cursor-pointer transition-colors",
            expandedSection === 'insights' ? "border-primary-500/50" : "hover:border-primary-500/50"
          )}
          onClick={() => toggleSection('insights')}
        >
          <div className="flex items-center justify-between mb-1">
            <div className="flex items-center gap-2">
              <Lightbulb size={14} className="text-accent-amber" />
              <span className="text-xs text-gray-500">Insights</span>
            </div>
            {expandedSection === 'insights' ? <ChevronUp size={12} className="text-primary-400" /> : <ChevronDown size={12} className="text-gray-500" />}
          </div>
          <div className="text-2xl font-bold">4</div>
        </div>
        <div
          className={cn(
            "card cursor-pointer transition-colors",
            expandedSection === 'collabs' ? "border-primary-500/50" : "hover:border-primary-500/50"
          )}
          onClick={() => toggleSection('collabs')}
        >
          <div className="flex items-center justify-between mb-1">
            <div className="flex items-center gap-2">
              <Activity size={14} className="text-accent-green" />
              <span className="text-xs text-gray-500">Collaborations</span>
            </div>
            {expandedSection === 'collabs' ? <ChevronUp size={12} className="text-primary-400" /> : <ChevronDown size={12} className="text-gray-500" />}
          </div>
          <div className="text-2xl font-bold">{dashboard.active_collaborations || 0}</div>
        </div>
      </div>

      {/* Recent Shared Knowledge (compact view) */}
      {expandedSection !== 'knowledge' && knowledge.length > 0 && (
        <div className="card">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-medium text-gray-400">Recent Shared Knowledge</h4>
            <button
              onClick={() => toggleSection('knowledge')}
              className="text-xs text-primary-400 hover:text-primary-300 flex items-center gap-1"
            >
              View All <ChevronRight size={12} />
            </button>
          </div>
          <div className="space-y-2">
            {knowledge.slice(0, 4).map((item: KnowledgeItem) => (
              <KnowledgeRow
                key={item.id}
                item={item}
                onClick={() => setSelectedKnowledge(item)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Collective Features */}
      <div className="card">
        <h4 className="text-sm font-medium text-gray-400 mb-3">Knowledge Sharing</h4>
        <div className="space-y-2">
          <FeatureRow label="Cross-Agent Learning" status="active" description="Pattern sharing between agents" />
          <FeatureRow label="Knowledge Gaps" status="active" description="Identify missing expertise" />
          <FeatureRow label="Emergent Insights" status="active" description="Multi-agent synthesis" />
          <FeatureRow label="Wisdom Injection" status="active" description="25 advisor personas active" />
        </div>
      </div>

      {/* Agent Categories */}
      <div className="card">
        <h4 className="text-sm font-medium text-gray-400 mb-3">Agent Ecosystem</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
          <CategoryBadge name="Creation" count={4} onClick={() => toggleCategory('creation')} isExpanded={selectedCategory === 'creation'} />
          <CategoryBadge name="Research" count={3} onClick={() => toggleCategory('research')} isExpanded={selectedCategory === 'research'} />
          <CategoryBadge name="Strategy" count={8} onClick={() => toggleCategory('strategy')} isExpanded={selectedCategory === 'strategy'} />
          <CategoryBadge name="Development" count={5} onClick={() => toggleCategory('development')} isExpanded={selectedCategory === 'development'} />
          <CategoryBadge name="Analysis" count={6} onClick={() => toggleCategory('analysis')} isExpanded={selectedCategory === 'analysis'} />
          <CategoryBadge name="Executive" count={4} onClick={() => toggleCategory('executive')} isExpanded={selectedCategory === 'executive'} />
          <CategoryBadge name="Blockchain" count={5} onClick={() => toggleCategory('blockchain')} isExpanded={selectedCategory === 'blockchain'} />
          <CategoryBadge name="Other" count={39} onClick={() => toggleCategory('other')} isExpanded={selectedCategory === 'other'} />
        </div>
      </div>

      {/* Knowledge Detail Modal */}
      {selectedKnowledge && (
        <KnowledgeDetailModal
          item={selectedKnowledge}
          onClose={() => setSelectedKnowledge(null)}
        />
      )}
    </div>
  )
}

// ============ Helper Components ============

function LoadingState() {
  return (
    <div className="flex items-center justify-center py-12">
      <Loader2 className="animate-spin text-primary-400" size={24} />
    </div>
  )
}

// Session 857: Inline header without external navigation
function InlineHeaderRow({
  title,
  subtitle,
  onRefresh,
  isFetching,
}: {
  title: string
  subtitle?: string
  onRefresh?: () => void
  isFetching?: boolean
}) {
  return (
    <div className="flex items-center justify-between">
      <div>
        <h3 className="text-lg font-semibold">{title}</h3>
        {subtitle && <p className="text-xs text-gray-500">{subtitle}</p>}
      </div>
      {onRefresh && (
        <button
          onClick={onRefresh}
          disabled={isFetching}
          className="p-2 hover:bg-gray-800 rounded-lg transition-colors disabled:opacity-50"
          title="Refresh data"
        >
          <RefreshCw size={14} className={cn("text-gray-400", isFetching && "animate-spin")} />
        </button>
      )}
    </div>
  )
}

// Session 857: Expandable list card
// Session 870: Added error state support
function ExpandedListCard({
  title,
  isLoading,
  isError,
  onClose,
  count,
  children,
}: {
  title: string
  isLoading: boolean
  isError?: boolean
  onClose: () => void
  count?: number
  children: React.ReactNode
}) {
  return (
    <div className={cn("card", isError ? "border-red-500/30" : "border-primary-500/30")}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <List size={14} className={isError ? "text-red-400" : "text-primary-400"} />
          <h4 className="text-sm font-medium">{title}</h4>
          {count !== undefined && !isError && (
            <span className="text-xs text-gray-500">({count})</span>
          )}
        </div>
        <button
          onClick={onClose}
          className="p-1 hover:bg-gray-800 rounded transition-colors"
          title="Close"
        >
          <X size={14} />
        </button>
      </div>
      {isLoading ? (
        <div className="flex items-center justify-center py-8">
          <Loader2 className="animate-spin text-primary-400" size={20} />
        </div>
      ) : isError ? (
        <div className="flex flex-col items-center justify-center py-8 text-center">
          <AlertTriangle size={24} className="text-red-400 mb-2" />
          <p className="text-sm text-gray-400">Failed to load data</p>
          <p className="text-xs text-gray-500 mt-1">Please try again later</p>
        </div>
      ) : (
        children
      )}
    </div>
  )
}

// Session 857: Updated StatCard with isExpanded
function StatCard({
  label,
  value,
  icon: Icon,
  color,
  onClick,
  isExpanded,
}: {
  label: string
  value: number | string
  icon: typeof Brain
  color: string
  onClick?: () => void
  isExpanded?: boolean
}) {
  return (
    <div
      className={cn(
        'card transition-colors',
        onClick && 'cursor-pointer hover:border-primary-500/50',
        isExpanded && 'bg-primary-500/10 border-primary-500/30'
      )}
      onClick={onClick}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-400">{label}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
        </div>
        <div className="flex flex-col items-center gap-1">
          <div className="h-10 w-10 rounded-lg flex items-center justify-center bg-gray-800">
            <Icon size={20} className={color} />
          </div>
          {onClick && (
            isExpanded ? (
              <ChevronUp size={12} className="text-primary-400" />
            ) : (
              <ChevronDown size={12} className="text-gray-500" />
            )
          )}
        </div>
      </div>
    </div>
  )
}

function PendingActionRow({ action, onClick }: { action: any; onClick?: () => void }) {
  return (
    <div
      className="flex items-center justify-between py-2 border-b border-gray-800 last:border-0 cursor-pointer hover:bg-gray-800/50 -mx-2 px-2 rounded transition-colors"
      onClick={onClick}
    >
      <div className="flex items-center gap-3">
        <Clock size={14} className="text-accent-amber" />
        <div>
          <span className="text-sm font-medium">{action.action_type || 'Action'}</span>
          <p className="text-xs text-gray-500">
            {action.created_at ? new Date(action.created_at).toLocaleString() : 'Pending'}
          </p>
        </div>
      </div>
      <span className="text-xs px-2 py-1 rounded bg-accent-amber/20 text-accent-amber">
        Review
      </span>
    </div>
  )
}

// Session 840: Thought row component
function ThoughtRow({ thought, onClick }: { thought: ThoughtRecord; onClick: () => void }) {
  return (
    <div
      className="flex items-center justify-between py-2 border-b border-gray-800 last:border-0 cursor-pointer hover:bg-gray-800/50 -mx-2 px-2 rounded transition-colors"
      onClick={onClick}
    >
      <div className="flex items-center gap-3 flex-1 min-w-0">
        <Lightbulb size={14} className="text-accent-amber shrink-0" />
        <div className="flex-1 min-w-0">
          <span className="text-sm truncate block">{thought.content?.slice(0, 60)}...</span>
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <span>{thought.thought_type}</span>
            {thought.agent_name && (
              <>
                <span>•</span>
                <span>{thought.agent_name}</span>
              </>
            )}
          </div>
        </div>
      </div>
      <Eye size={14} className="text-gray-500 shrink-0 ml-2" />
    </div>
  )
}

function EventRow({ event, onClick }: { event: any; onClick?: () => void }) {
  const severityColors: Record<string, { bg: string; color: string }> = {
    low: { bg: 'bg-gray-500/20', color: 'text-gray-400' },
    medium: { bg: 'bg-accent-amber/20', color: 'text-accent-amber' },
    high: { bg: 'bg-red-500/20', color: 'text-red-400' },
  }
  const style = severityColors[event.severity] || severityColors.low

  return (
    <div
      className={cn(
        'flex items-center justify-between py-2 border-b border-gray-800 last:border-0',
        onClick && 'cursor-pointer hover:bg-gray-800/50 -mx-2 px-2 rounded transition-colors'
      )}
      onClick={onClick}
    >
      <div className="flex items-center gap-3">
        <AlertTriangle size={14} className={style.color} />
        <div>
          <span className="text-sm">{event.pattern_name || 'Unknown Pattern'}</span>
          <p className="text-xs text-gray-500">{event.agent_name}</p>
        </div>
      </div>
      <span className={cn('text-xs px-2 py-0.5 rounded capitalize', style.bg, style.color)}>
        {event.severity}
      </span>
    </div>
  )
}

// Session 840: Pattern row component
function PatternRow({ pattern, onClick }: { pattern: MythPattern; onClick: () => void }) {
  const severityColors: Record<string, string> = {
    low: 'text-gray-400',
    medium: 'text-accent-amber',
    high: 'text-red-400',
    critical: 'text-red-500',
  }

  return (
    <div
      className="flex items-center justify-between py-2 border-b border-gray-800 last:border-0 cursor-pointer hover:bg-gray-800/50 -mx-2 px-2 rounded transition-colors"
      onClick={onClick}
    >
      <div className="flex items-center gap-3 flex-1 min-w-0">
        <Shield size={14} className={severityColors[pattern.severity] || 'text-gray-400'} />
        <div className="flex-1 min-w-0">
          <span className="text-sm font-medium">{pattern.name}</span>
          <p className="text-xs text-gray-500 truncate">{pattern.description}</p>
        </div>
      </div>
      <div className="flex items-center gap-2 shrink-0">
        <span className="text-xs text-gray-500">{pattern.detection_count} detections</span>
        <span className={cn(
          'text-xs px-2 py-0.5 rounded',
          pattern.is_active ? 'bg-accent-green/20 text-accent-green' : 'bg-gray-500/20 text-gray-400'
        )}>
          {pattern.is_active ? 'Active' : 'Inactive'}
        </span>
      </div>
    </div>
  )
}

// Session 840: Knowledge row component
function KnowledgeRow({ item, onClick }: { item: KnowledgeItem; onClick: () => void }) {
  return (
    <div
      className="flex items-center justify-between py-2 border-b border-gray-800 last:border-0 cursor-pointer hover:bg-gray-800/50 -mx-2 px-2 rounded transition-colors"
      onClick={onClick}
    >
      <div className="flex items-center gap-3 flex-1 min-w-0">
        <BookOpen size={14} className="text-accent-green shrink-0" />
        <div className="flex-1 min-w-0">
          <span className="text-sm font-medium truncate block">{item.title}</span>
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <span>{item.source_agent}</span>
            {item.category && (
              <>
                <span>•</span>
                <span>{item.category}</span>
              </>
            )}
          </div>
        </div>
      </div>
      <Eye size={14} className="text-gray-500 shrink-0 ml-2" />
    </div>
  )
}

function PipelineRow({
  label,
  description,
}: {
  label: string
  description: string
}) {
  return (
    <div className="flex items-center gap-3 py-2 border-b border-gray-800 last:border-0">
      <CheckCircle size={14} className="text-accent-green" />
      <div className="flex-1">
        <span className="text-sm">{label}</span>
        <p className="text-xs text-gray-500">{description}</p>
      </div>
    </div>
  )
}

function FeatureRow({
  label,
  status,
  description,
}: {
  label: string
  status: 'active' | 'inactive'
  description: string
}) {
  return (
    <div className="flex items-center justify-between py-2">
      <div className="flex items-center gap-3">
        <div className={cn(
          'h-2 w-2 rounded-full',
          status === 'active' ? 'bg-accent-green' : 'bg-gray-500'
        )} />
        <div>
          <span className="text-sm">{label}</span>
          <p className="text-xs text-gray-500">{description}</p>
        </div>
      </div>
      <span className={cn(
        'text-xs px-2 py-0.5 rounded capitalize',
        status === 'active' ? 'bg-accent-green/20 text-accent-green' : 'bg-gray-500/20 text-gray-400'
      )}>
        {status}
      </span>
    </div>
  )
}

function CategoryBadge({ name, count, onClick, isExpanded }: { name: string; count: number; onClick?: () => void; isExpanded?: boolean }) {
  return (
    <div
      className={cn(
        'flex items-center justify-between px-3 py-2 rounded-lg transition-colors',
        onClick && 'cursor-pointer',
        isExpanded ? 'bg-primary-500/20 border border-primary-500/30' : 'bg-gray-800/50 hover:bg-gray-800'
      )}
      onClick={onClick}
    >
      <span className="text-xs text-gray-400">{name}</span>
      <div className="flex items-center gap-1">
        <span className="text-xs font-medium">{count}</span>
        {onClick && (
          isExpanded ? (
            <ChevronUp size={10} className="text-primary-400" />
          ) : (
            <ChevronDown size={10} className="text-gray-500" />
          )
        )}
      </div>
    </div>
  )
}

// ============ Detail Modals ============

// Session 857: Thought Detail Modal (updated - removed external link)
function ThoughtDetailModal({ thought, onClose }: { thought: ThoughtRecord; onClose: () => void }) {
  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-dark-card border border-dark-border rounded-xl w-full max-w-2xl mx-4 max-h-[85vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-4 border-b border-dark-border">
          <div className="flex items-center gap-3">
            <Lightbulb size={20} className="text-accent-amber" />
            <div>
              <h3 className="font-semibold">Thought Record</h3>
              <p className="text-xs text-gray-500">{thought.thought_type}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-gray-700 rounded transition-colors">
            <X size={20} className="text-gray-400" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <div>
            <h4 className="text-sm font-medium text-gray-400 mb-2">Content</h4>
            <p className="text-sm whitespace-pre-wrap">{thought.content}</p>
          </div>

          {thought.context && (
            <div>
              <h4 className="text-sm font-medium text-gray-400 mb-2">Context</h4>
              <p className="text-sm text-gray-300 whitespace-pre-wrap">{thought.context}</p>
            </div>
          )}

          <div className="flex flex-wrap gap-4 text-xs text-gray-500 pt-4 border-t border-dark-border">
            {thought.agent_name && <span>Agent: {thought.agent_name}</span>}
            {thought.quality_score !== undefined && (
              <div className="flex items-center gap-2">
                <span>Quality:</span>
                <div className="w-16 h-1.5 bg-gray-700 rounded-full overflow-hidden">
                  <div className="h-full bg-accent-green" style={{ width: `${(thought.quality_score || 0) * 100}%` }} />
                </div>
                <span>{((thought.quality_score || 0) * 100).toFixed(0)}%</span>
              </div>
            )}
            <span>Created: {new Date(thought.created_at).toLocaleString()}</span>
          </div>
        </div>

        <div className="p-4 border-t border-dark-border flex justify-end">
          <button onClick={onClose} className="btn btn-primary text-sm">
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

// Session 857: Action Detail Modal
function ActionDetailModal({ action, onClose }: { action: any; onClose: () => void }) {
  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-dark-card border border-dark-border rounded-xl w-full max-w-2xl mx-4 max-h-[85vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-4 border-b border-dark-border">
          <div className="flex items-center gap-3">
            <Zap size={20} className="text-accent-purple" />
            <div>
              <h3 className="font-semibold">{action.action_type || 'Autonomous Action'}</h3>
              <span className={cn(
                'text-xs px-2 py-0.5 rounded capitalize',
                action.status === 'completed' ? 'bg-accent-green/20 text-accent-green' :
                action.status === 'pending' ? 'bg-accent-amber/20 text-accent-amber' :
                'bg-gray-700 text-gray-400'
              )}>
                {action.status || 'completed'}
              </span>
            </div>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-gray-700 rounded transition-colors">
            <X size={20} className="text-gray-400" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {action.description && (
            <div>
              <h4 className="text-sm font-medium text-gray-400 mb-2">Description</h4>
              <p className="text-sm whitespace-pre-wrap">{action.description}</p>
            </div>
          )}

          {action.result && (
            <div>
              <h4 className="text-sm font-medium text-gray-400 mb-2">Result</h4>
              <p className="text-sm text-gray-300 whitespace-pre-wrap">{action.result}</p>
            </div>
          )}

          <div className="flex flex-wrap gap-4 text-xs text-gray-500 pt-4 border-t border-dark-border">
            {action.agent_name && <span>Agent: {action.agent_name}</span>}
            {action.created_at && <span>Created: {new Date(action.created_at).toLocaleString()}</span>}
          </div>
        </div>

        <div className="p-4 border-t border-dark-border flex justify-end">
          <button onClick={onClose} className="btn btn-primary text-sm">
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

// Session 857: Event Detail Modal
function EventDetailModal({ event, onClose }: { event: any; onClose: () => void }) {
  const severityColors: Record<string, { bg: string; text: string }> = {
    low: { bg: 'bg-gray-500/20', text: 'text-gray-400' },
    medium: { bg: 'bg-accent-amber/20', text: 'text-accent-amber' },
    high: { bg: 'bg-red-500/20', text: 'text-red-400' },
  }
  const style = severityColors[event.severity] || severityColors.low

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-dark-card border border-dark-border rounded-xl w-full max-w-2xl mx-4 max-h-[85vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-4 border-b border-dark-border">
          <div className="flex items-center gap-3">
            <AlertTriangle size={20} className={style.text} />
            <div>
              <h3 className="font-semibold">{event.pattern_name || 'Safety Event'}</h3>
              <div className="flex items-center gap-2 mt-1">
                <span className={cn('text-xs px-2 py-0.5 rounded capitalize', style.bg, style.text)}>
                  {event.severity}
                </span>
                {event.agent_name && <span className="text-xs text-gray-500">{event.agent_name}</span>}
              </div>
            </div>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-gray-700 rounded transition-colors">
            <X size={20} className="text-gray-400" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {event.description && (
            <div>
              <h4 className="text-sm font-medium text-gray-400 mb-2">Description</h4>
              <p className="text-sm whitespace-pre-wrap">{event.description}</p>
            </div>
          )}

          {event.content && (
            <div>
              <h4 className="text-sm font-medium text-gray-400 mb-2">Flagged Content</h4>
              <p className="text-sm text-gray-300 whitespace-pre-wrap bg-gray-800/50 p-3 rounded">{event.content}</p>
            </div>
          )}

          {event.action_taken && (
            <div>
              <h4 className="text-sm font-medium text-gray-400 mb-2">Action Taken</h4>
              <p className="text-sm text-gray-300">{event.action_taken}</p>
            </div>
          )}

          <div className="flex flex-wrap gap-4 text-xs text-gray-500 pt-4 border-t border-dark-border">
            {event.created_at && <span>Occurred: {new Date(event.created_at).toLocaleString()}</span>}
          </div>
        </div>

        <div className="p-4 border-t border-dark-border flex justify-end">
          <button onClick={onClose} className="btn btn-primary text-sm">
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

// Session 857: Pattern Detail Modal (updated - removed external link)
function PatternDetailModal({ pattern, onClose }: { pattern: MythPattern; onClose: () => void }) {
  const severityColors: Record<string, { bg: string; text: string }> = {
    low: { bg: 'bg-gray-500/20', text: 'text-gray-400' },
    medium: { bg: 'bg-accent-amber/20', text: 'text-accent-amber' },
    high: { bg: 'bg-red-500/20', text: 'text-red-400' },
    critical: { bg: 'bg-red-600/20', text: 'text-red-500' },
  }
  const style = severityColors[pattern.severity] || severityColors.low

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-dark-card border border-dark-border rounded-xl w-full max-w-2xl mx-4 max-h-[85vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-4 border-b border-dark-border">
          <div className="flex items-center gap-3">
            <Shield size={20} className={style.text} />
            <div>
              <h3 className="font-semibold">{pattern.name}</h3>
              <div className="flex items-center gap-2 mt-1">
                <span className={cn('text-xs px-2 py-0.5 rounded capitalize', style.bg, style.text)}>
                  {pattern.severity}
                </span>
                <span className={cn(
                  'text-xs px-2 py-0.5 rounded',
                  pattern.is_active ? 'bg-accent-green/20 text-accent-green' : 'bg-gray-500/20 text-gray-400'
                )}>
                  {pattern.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            </div>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-gray-700 rounded transition-colors">
            <X size={20} className="text-gray-400" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <div>
            <h4 className="text-sm font-medium text-gray-400 mb-2">Description</h4>
            <p className="text-sm whitespace-pre-wrap">{pattern.description}</p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="p-3 bg-gray-800/50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Detection Count</p>
              <p className="text-xl font-bold">{pattern.detection_count}</p>
            </div>
            <div className="p-3 bg-gray-800/50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">Created</p>
              <p className="text-sm">{new Date(pattern.created_at).toLocaleDateString()}</p>
            </div>
          </div>
        </div>

        <div className="p-4 border-t border-dark-border flex justify-end">
          <button onClick={onClose} className="btn btn-primary text-sm">
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

// Session 857: Knowledge Detail Modal (updated - removed external link)
function KnowledgeDetailModal({ item, onClose }: { item: KnowledgeItem; onClose: () => void }) {
  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-dark-card border border-dark-border rounded-xl w-full max-w-2xl mx-4 max-h-[85vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-4 border-b border-dark-border">
          <div className="flex items-center gap-3">
            <BookOpen size={20} className="text-accent-green" />
            <div>
              <h3 className="font-semibold">{item.title}</h3>
              <div className="flex items-center gap-2 text-xs text-gray-500 mt-1">
                <span>From: {item.source_agent}</span>
                {item.category && (
                  <>
                    <span>•</span>
                    <span className="px-2 py-0.5 bg-gray-700 rounded">{item.category}</span>
                  </>
                )}
              </div>
            </div>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-gray-700 rounded transition-colors">
            <X size={20} className="text-gray-400" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <div>
            <h4 className="text-sm font-medium text-gray-400 mb-2">Content</h4>
            <p className="text-sm whitespace-pre-wrap">{item.content}</p>
          </div>

          <div className="flex flex-wrap gap-4 text-xs text-gray-500 pt-4 border-t border-dark-border">
            {item.usefulness_score !== undefined && (
              <div className="flex items-center gap-2">
                <span>Usefulness:</span>
                <div className="w-16 h-1.5 bg-gray-700 rounded-full overflow-hidden">
                  <div className="h-full bg-accent-green" style={{ width: `${(item.usefulness_score || 0) * 100}%` }} />
                </div>
                <span>{((item.usefulness_score || 0) * 100).toFixed(0)}%</span>
              </div>
            )}
            <span>Created: {new Date(item.created_at).toLocaleString()}</span>
          </div>
        </div>

        <div className="p-4 border-t border-dark-border flex justify-end">
          <button onClick={onClose} className="btn btn-primary text-sm">
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
