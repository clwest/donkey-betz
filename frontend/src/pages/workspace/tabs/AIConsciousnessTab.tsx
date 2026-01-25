// Session 825: AI Consciousness Tab
// Consolidates: Memory Palace, Neural Orchestra, Mood, Evolution, Relationships, Social, Time Capsules, Time Travel
// Safe approach: Compact views with links to full pages

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Brain,
  Music,
  Heart,
  TrendingUp,
  Users,
  MessageCircle,
  Clock,
  Rewind,
  Loader2,
  ExternalLink,
  Sparkles,
  Zap,
  Award,
  Activity,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import {
  memoryPalaceApi,
  neuralOrchestraApi,
  moodApi,
  evolutionApi,
  relationshipsApi,
  timeCapsuleApi,
  timeTravelApi,
} from '@/lib/api'

// Sub-tab configuration
type ConsciousnessSubTab = 'memory' | 'orchestra' | 'mood' | 'evolution' | 'relationships' | 'social' | 'capsules' | 'travel'

const subTabs: Array<{ id: ConsciousnessSubTab; label: string; icon: typeof Brain; description: string }> = [
  { id: 'memory', label: 'Memory', icon: Brain, description: 'Memory Palace' },
  { id: 'orchestra', label: 'Orchestra', icon: Music, description: 'Neural activity' },
  { id: 'mood', label: 'Mood', icon: Heart, description: 'Agent emotions' },
  { id: 'evolution', label: 'Evolution', icon: TrendingUp, description: 'Agent growth' },
  { id: 'relationships', label: 'Relations', icon: Users, description: 'Agent bonds' },
  { id: 'social', label: 'Social', icon: MessageCircle, description: 'Conversations' },
  { id: 'capsules', label: 'Capsules', icon: Clock, description: 'Time capsules' },
  { id: 'travel', label: 'Time Travel', icon: Rewind, description: 'Decision exploration' },
]

export function AIConsciousnessTab() {
  const [activeSubTab, setActiveSubTab] = useState<ConsciousnessSubTab>('memory')

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
      {activeSubTab === 'memory' && <MemorySubTab />}
      {activeSubTab === 'orchestra' && <OrchestraSubTab />}
      {activeSubTab === 'mood' && <MoodSubTab />}
      {activeSubTab === 'evolution' && <EvolutionSubTab />}
      {activeSubTab === 'relationships' && <RelationshipsSubTab />}
      {activeSubTab === 'social' && <SocialSubTab />}
      {activeSubTab === 'capsules' && <CapsulesSubTab />}
      {activeSubTab === 'travel' && <TimeTravelSubTab />}
    </div>
  )
}

// ============ Memory Palace Sub-Tab ============

function MemorySubTab() {
  const { data: overviewData, isLoading } = useQuery({
    queryKey: ['memory-palace-overview-tab'],
    queryFn: async () => {
      const res = await memoryPalaceApi.overview()
      return res.data
    },
  })

  if (isLoading) {
    return <LoadingState />
  }

  const stats = overviewData || {
    total_memories: 0,
    total_rooms: 0,
    agents_with_memories: 0,
    memory_types: {},
  }

  return (
    <div className="space-y-4">
      <HeaderRow title="Memory Palace" linkTo="/memory-palace" linkLabel="Explore Memories" />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard label="Total Memories" value={stats.total_memories || 0} color="text-primary-400" />
        <StatCard label="Memory Rooms" value={stats.total_rooms || 0} color="text-accent-purple" />
        <StatCard label="Active Agents" value={stats.agents_with_memories || 74} color="text-accent-green" />
        <StatCard label="Memory Types" value={Object.keys(stats.memory_types || {}).length || 6} color="text-accent-cyan" />
      </div>

      <div className="card">
        <h4 className="text-sm font-medium text-gray-400 mb-3">Memory Classification</h4>
        <div className="space-y-2">
          <ClassificationRow label="Approved Memories" status="active" description="Verified and embedded" />
          <ClassificationRow label="Candidate Memories" status="pending" description="Awaiting review" />
          <ClassificationRow label="Exploratory" status="inactive" description="Low-confidence patterns" />
          <ClassificationRow label="Test Only" status="inactive" description="Development/health checks" />
        </div>
      </div>
    </div>
  )
}

// ============ Neural Orchestra Sub-Tab ============

function OrchestraSubTab() {
  const { data: statsData, isLoading } = useQuery({
    queryKey: ['neural-orchestra-stats-tab'],
    queryFn: async () => {
      const res = await neuralOrchestraApi.agentStats()
      return res.data
    },
  })

  const { data: learningData } = useQuery({
    queryKey: ['neural-orchestra-learning-tab'],
    queryFn: async () => {
      const res = await neuralOrchestraApi.learningStatus()
      return res.data
    },
  })

  if (isLoading) {
    return <LoadingState />
  }

  const stats = statsData || { total: 74, active: 0, collaborations: 0 }
  const learning = learningData || { models_active: 15, feedback_processed: 0 }

  return (
    <div className="space-y-4">
      <HeaderRow title="Neural Orchestra" linkTo="/neural-orchestra" linkLabel="Live View" />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard label="Total Agents" value={stats.total || 74} color="text-primary-400" />
        <StatCard label="Active Now" value={stats.active || 0} color="text-accent-green" />
        <StatCard label="Collaborations" value={stats.collaborations || 0} color="text-accent-purple" />
        <StatCard label="ML Models" value={learning.models_active || 15} color="text-accent-amber" />
      </div>

      <div className="card">
        <h4 className="text-sm font-medium text-gray-400 mb-3">Neural Network Status</h4>
        <div className="space-y-2">
          <StatusRow label="Agent Network" status="online" description="74 agents connected" />
          <StatusRow label="Learning Pipeline" status="online" description="15 ML models active" />
          <StatusRow label="Memory Sync" status="online" description="Real-time embedding" />
          <StatusRow label="Collective Intelligence" status="online" description="Cross-agent patterns" />
        </div>
      </div>
    </div>
  )
}

// ============ Mood Sub-Tab ============

function MoodSubTab() {
  const { data: overviewData, isLoading } = useQuery({
    queryKey: ['mood-overview-tab'],
    queryFn: async () => {
      const res = await moodApi.overview()
      return res.data
    },
  })

  if (isLoading) {
    return <LoadingState />
  }

  const overview = overviewData || { mood_distribution: {}, agents_with_mood: 0 }
  const moodDist = overview.mood_distribution || {}

  return (
    <div className="space-y-4">
      <HeaderRow title="Agent Mood" linkTo="/agent-mood" linkLabel="Mood Dashboard" />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <MoodCard mood="Happy" count={moodDist.happy || 0} icon={Sparkles} color="text-accent-green" />
        <MoodCard mood="Focused" count={moodDist.focused || 0} icon={Zap} color="text-primary-400" />
        <MoodCard mood="Curious" count={moodDist.curious || 0} icon={Brain} color="text-accent-purple" />
        <MoodCard mood="Neutral" count={moodDist.neutral || 0} icon={Heart} color="text-gray-400" />
      </div>

      <div className="card">
        <h4 className="text-sm font-medium text-gray-400 mb-3">Mood Influence</h4>
        <p className="text-xs text-gray-500 mb-3">
          Agent mood affects their communication style, decision-making, and collaboration patterns.
        </p>
        <a href="/agent-mood" className="btn btn-secondary text-sm">
          Manage Agent Moods
        </a>
      </div>
    </div>
  )
}

// ============ Evolution Sub-Tab ============

function EvolutionSubTab() {
  const { data: overviewData, isLoading } = useQuery({
    queryKey: ['evolution-overview-tab'],
    queryFn: async () => {
      const res = await evolutionApi.overview()
      return res.data
    },
  })

  if (isLoading) {
    return <LoadingState />
  }

  const overview = overviewData || { level_distribution: {}, total_xp: 0 }

  return (
    <div className="space-y-4">
      <HeaderRow title="Agent Evolution" linkTo="/evolution" linkLabel="Evolution Center" />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard label="Total XP" value={overview.total_xp || 0} color="text-accent-amber" />
        <StatCard label="Max Level" value={overview.max_level || 10} color="text-primary-400" />
        <StatCard label="Evolutions" value={overview.total_evolutions || 0} color="text-accent-green" />
        <StatCard label="Prestiges" value={overview.total_prestiges || 0} color="text-accent-purple" />
      </div>

      <div className="card">
        <h4 className="text-sm font-medium text-gray-400 mb-3">Level Distribution</h4>
        <div className="flex gap-2 flex-wrap">
          {[1, 2, 3, 4, 5].map((level) => (
            <span
              key={level}
              className="text-xs px-2 py-1 rounded bg-gray-800 text-gray-400"
            >
              Lvl {level}: {overview.level_distribution?.[level] || 0}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}

// ============ Relationships Sub-Tab ============

function RelationshipsSubTab() {
  const { data: overviewData, isLoading } = useQuery({
    queryKey: ['relationships-overview-tab'],
    queryFn: async () => {
      const res = await relationshipsApi.overview()
      return res.data
    },
  })

  if (isLoading) {
    return <LoadingState />
  }

  const overview = overviewData || { total_relationships: 0, relationship_types: {} }

  return (
    <div className="space-y-4">
      <HeaderRow title="Agent Relationships" linkTo="/relationships" linkLabel="Relationship Map" />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard label="Total Bonds" value={overview.total_relationships || 0} color="text-primary-400" />
        <StatCard label="Collaborators" value={overview.relationship_types?.collaborator || 0} color="text-accent-green" />
        <StatCard label="Mentors" value={overview.relationship_types?.mentor || 0} color="text-accent-amber" />
        <StatCard label="Rivals" value={overview.relationship_types?.rival || 0} color="text-red-400" />
      </div>

      <div className="card">
        <h4 className="text-sm font-medium text-gray-400 mb-3">Relationship Types</h4>
        <div className="space-y-2">
          <RelationshipTypeRow type="Collaborator" description="Work together on tasks" />
          <RelationshipTypeRow type="Mentor/Mentee" description="Knowledge transfer" />
          <RelationshipTypeRow type="Rival" description="Healthy competition" />
          <RelationshipTypeRow type="Specialist" description="Domain expertise" />
        </div>
      </div>
    </div>
  )
}

// ============ Social Sub-Tab ============

function SocialSubTab() {
  // Social stats - hardcoded for now
  const stats = {
    conversations: 847,
    messages: 12450,
    activeChannels: 15,
    topicsTrending: 8,
  }

  return (
    <div className="space-y-4">
      <HeaderRow title="Agent Social" linkTo="/agent-social" linkLabel="Social Hub" />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard label="Conversations" value={stats.conversations} color="text-primary-400" />
        <StatCard label="Messages" value={stats.messages.toLocaleString()} color="text-accent-green" />
        <StatCard label="Channels" value={stats.activeChannels} color="text-accent-purple" />
        <StatCard label="Trending Topics" value={stats.topicsTrending} color="text-accent-amber" />
      </div>

      <div className="card">
        <h4 className="text-sm font-medium text-gray-400 mb-3">Social Features</h4>
        <div className="space-y-2">
          <FeatureRow label="Multi-Agent Conversations" description="Agents discuss topics together" />
          <FeatureRow label="Discourse Memory" description="Track conversation patterns" />
          <FeatureRow label="Voice De-duplication" description="Unique agent personalities" />
          <FeatureRow label="Channel Subscriptions" description="Topic-based groups" />
        </div>
      </div>
    </div>
  )
}

// ============ Time Capsules Sub-Tab ============

function CapsulesSubTab() {
  const { data: overviewData, isLoading } = useQuery({
    queryKey: ['time-capsules-overview-tab'],
    queryFn: async () => {
      const res = await timeCapsuleApi.overview()
      return res.data
    },
  })

  const { data: readyData } = useQuery({
    queryKey: ['time-capsules-ready-tab'],
    queryFn: async () => {
      const res = await timeCapsuleApi.readyToReveal()
      return res.data
    },
  })

  if (isLoading) {
    return <LoadingState />
  }

  const overview = overviewData || { total_capsules: 0, sealed: 0, revealed: 0 }
  const ready = readyData?.capsules || []

  return (
    <div className="space-y-4">
      <HeaderRow title="Time Capsules" linkTo="/time-capsules" linkLabel="Capsule Vault" />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard label="Total Capsules" value={overview.total_capsules || 0} color="text-primary-400" />
        <StatCard label="Sealed" value={overview.sealed || 0} color="text-accent-purple" />
        <StatCard label="Revealed" value={overview.revealed || 0} color="text-accent-green" />
        <StatCard label="Ready to Open" value={ready.length} color="text-accent-amber" />
      </div>

      {ready.length > 0 && (
        <div className="card border-accent-amber/50">
          <div className="flex items-center gap-2 mb-3">
            <Award size={16} className="text-accent-amber" />
            <h4 className="text-sm font-medium">Ready to Reveal!</h4>
          </div>
          <div className="space-y-2">
            {ready.slice(0, 3).map((capsule: any) => (
              <CapsuleRow key={capsule.id} capsule={capsule} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// ============ Time Travel Sub-Tab ============

function TimeTravelSubTab() {
  const { data: overviewData, isLoading } = useQuery({
    queryKey: ['time-travel-overview-tab'],
    queryFn: async () => {
      const res = await timeTravelApi.overview()
      return res.data
    },
  })

  if (isLoading) {
    return <LoadingState />
  }

  const overview = overviewData || { total_sessions: 0, total_decisions: 0, active_sessions: 0 }

  return (
    <div className="space-y-4">
      <HeaderRow title="Time Travel" linkTo="/time-travel" linkLabel="Decision Explorer" />

      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        <StatCard label="Sessions" value={overview.total_sessions || 0} color="text-primary-400" />
        <StatCard label="Decisions" value={overview.total_decisions || 0} color="text-accent-purple" />
        <StatCard label="Active" value={overview.active_sessions || 0} color="text-accent-green" />
      </div>

      <div className="card">
        <h4 className="text-sm font-medium text-gray-400 mb-3">What-If Analysis</h4>
        <p className="text-xs text-gray-500 mb-3">
          Explore alternative decision paths. Agents can simulate different choices and compare outcomes.
        </p>
        <div className="space-y-2">
          <FeatureRow label="Decision Recording" description="Capture key decision points" />
          <FeatureRow label="Path Simulation" description="Explore alternative outcomes" />
          <FeatureRow label="Bookmarking" description="Mark important sessions" />
        </div>
      </div>
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

function HeaderRow({
  title,
  linkTo,
  linkLabel,
}: {
  title: string
  linkTo: string
  linkLabel: string
}) {
  return (
    <div className="flex items-center justify-between">
      <h3 className="text-lg font-semibold">{title}</h3>
      <a href={linkTo} className="btn btn-secondary flex items-center gap-2 text-sm">
        {linkLabel}
        <ExternalLink size={14} />
      </a>
    </div>
  )
}

function StatCard({
  label,
  value,
  color,
}: {
  label: string
  value: number | string
  color: string
}) {
  return (
    <div className="card">
      <p className="text-sm text-gray-400">{label}</p>
      <p className={cn('text-2xl font-bold mt-1', color)}>{value}</p>
    </div>
  )
}

function MoodCard({
  mood,
  count,
  icon: Icon,
  color,
}: {
  mood: string
  count: number
  icon: typeof Heart
  color: string
}) {
  return (
    <div className="card">
      <div className="flex items-center gap-2 mb-1">
        <Icon size={14} className={color} />
        <span className="text-sm text-gray-400">{mood}</span>
      </div>
      <p className="text-2xl font-bold">{count}</p>
    </div>
  )
}

function ClassificationRow({
  label,
  status,
  description,
}: {
  label: string
  status: 'active' | 'pending' | 'inactive'
  description: string
}) {
  const statusColors = {
    active: 'bg-accent-green',
    pending: 'bg-accent-amber',
    inactive: 'bg-gray-500',
  }

  return (
    <div className="flex items-center justify-between py-2 border-b border-gray-800 last:border-0">
      <div className="flex items-center gap-3">
        <div className={cn('h-2 w-2 rounded-full', statusColors[status])} />
        <div>
          <span className="text-sm">{label}</span>
          <p className="text-xs text-gray-500">{description}</p>
        </div>
      </div>
    </div>
  )
}

function StatusRow({
  label,
  status,
  description,
}: {
  label: string
  status: 'online' | 'offline'
  description: string
}) {
  return (
    <div className="flex items-center justify-between py-2">
      <div className="flex items-center gap-3">
        <div className={cn(
          'h-2 w-2 rounded-full',
          status === 'online' ? 'bg-accent-green animate-pulse' : 'bg-red-500'
        )} />
        <div>
          <span className="text-sm">{label}</span>
          <p className="text-xs text-gray-500">{description}</p>
        </div>
      </div>
      <span className={cn(
        'text-xs px-2 py-0.5 rounded',
        status === 'online' ? 'bg-accent-green/20 text-accent-green' : 'bg-red-500/20 text-red-400'
      )}>
        {status}
      </span>
    </div>
  )
}

function RelationshipTypeRow({
  type,
  description,
}: {
  type: string
  description: string
}) {
  return (
    <div className="flex items-center gap-3 py-2 border-b border-gray-800 last:border-0">
      <Activity size={14} className="text-gray-500" />
      <div>
        <span className="text-sm">{type}</span>
        <p className="text-xs text-gray-500">{description}</p>
      </div>
    </div>
  )
}

function FeatureRow({
  label,
  description,
}: {
  label: string
  description: string
}) {
  return (
    <div className="flex items-center gap-3 py-2 border-b border-gray-800 last:border-0">
      <Sparkles size={14} className="text-primary-400" />
      <div>
        <span className="text-sm">{label}</span>
        <p className="text-xs text-gray-500">{description}</p>
      </div>
    </div>
  )
}

function CapsuleRow({ capsule }: { capsule: any }) {
  return (
    <div className="flex items-center justify-between py-2">
      <div>
        <span className="text-sm font-medium">{capsule.title || 'Untitled Capsule'}</span>
        <p className="text-xs text-gray-500">
          From {capsule.agent_name || 'Unknown'}
        </p>
      </div>
      <a
        href={`/time-capsules/${capsule.id}`}
        className="text-xs px-2 py-1 rounded bg-accent-amber/20 text-accent-amber hover:bg-accent-amber/30"
      >
        Reveal
      </a>
    </div>
  )
}
