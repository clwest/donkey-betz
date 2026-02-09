// Session 870: Learning Journey Dashboard Tab
// Session 956: Added Learning Loop Effectiveness sub-tab
// Shows user's learning journeys, progress, achievements, and available templates
import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  GraduationCap,
  Trophy,
  Flame,
  Target,
  Clock,
  CheckCircle2,
  Play,
  Pause,
  BookOpen,
  ChevronRight,
  Loader2,
  AlertTriangle,
  RefreshCw,
  X,
  Plus,
  Star,
  Zap,
  Award,
  TrendingUp,
  Brain,
  Activity,
  BarChart3,
  ThumbsUp,
  ThumbsDown,
  Sparkles,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { api } from '@/lib/api'

// Sub-tab configuration
type LearningSubTab = 'dashboard' | 'journeys' | 'templates' | 'effectiveness'

const subTabs: Array<{ id: LearningSubTab; label: string; icon: typeof GraduationCap }> = [
  { id: 'dashboard', label: 'Dashboard', icon: TrendingUp },
  { id: 'journeys', label: 'My Journeys', icon: BookOpen },
  { id: 'templates', label: 'Templates', icon: Target },
  { id: 'effectiveness', label: 'AI Learning', icon: Brain },
]

// Types
interface LearningJourney {
  id: string
  title: string
  description: string
  topic: string
  status: 'active' | 'paused' | 'completed' | 'abandoned'
  progress: number
  current_step: number
  total_steps: number
  estimated_hours: number
  goals: string[]
  started_at: string
  completed_at: string | null
  steps: LearningStep[]
}

interface LearningStep {
  step_number: number
  title: string
  description: string
  status: 'pending' | 'in_progress' | 'completed' | 'skipped'
  started_at: string | null
  completed_at: string | null
  duration_minutes: number
  notes: string
}

interface LearningTemplate {
  id: string
  name: string
  description: string
  category: string
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  estimated_hours: number
  steps_count: number
  popularity: number
  tags: string[]
}

interface Achievement {
  id: string
  name: string
  description: string
  icon: string
  earned_at: string | null
  progress: number
  total: number
}

interface Analytics {
  total_journeys: number
  completed_journeys: number
  total_steps_completed: number
  total_hours_spent: number
  current_streak: number
  longest_streak: number
  achievements_earned: number
}

// Session 956: Learning Loop Effectiveness Types
interface LearningPattern {
  id: string
  description: string
  effectiveness: number
  times_applied: number
  pattern_type: string
  confidence?: number
  created_at?: string
}

interface PatternTypeStats {
  pattern_type: string
  count: number
  avg_confidence: number
}

interface LearningLoopStats {
  total_active_learnings: number
  total_applied: number
  total_successful: number
  overall_effectiveness: number
  applied_patterns_count: number
  most_effective: LearningPattern[]
  least_effective: LearningPattern[]
  recent_learnings: LearningPattern[]
  by_pattern_type: PatternTypeStats[]
  timestamp: string
}

export function LearningJourneyTab() {
  const [activeSubTab, setActiveSubTab] = useState<LearningSubTab>('dashboard')

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
      {activeSubTab === 'dashboard' && <DashboardSubTab />}
      {activeSubTab === 'journeys' && <JourneysSubTab />}
      {activeSubTab === 'templates' && <TemplatesSubTab />}
      {activeSubTab === 'effectiveness' && <EffectivenessSubTab />}
    </div>
  )
}

// ============ Dashboard Sub-Tab ============

function DashboardSubTab() {
  const { data: analytics, isLoading, isError, refetch } = useQuery({
    queryKey: ['learning-analytics'],
    queryFn: async () => {
      const res = await api.get('/learning/journeys/analytics/')
      return res.data as Analytics
    },
  })

  const { data: achievementsData } = useQuery({
    queryKey: ['learning-achievements'],
    queryFn: async () => {
      const res = await api.get('/learning/achievements/')
      return res.data as { achievements: Achievement[]; total_points: number }
    },
  })

  const { data: activeJourneys } = useQuery({
    queryKey: ['learning-journeys-active'],
    queryFn: async () => {
      const res = await api.get('/learning/journeys/active/')
      return res.data as { journeys: LearningJourney[]; total: number }
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="animate-spin text-primary-400" size={24} />
      </div>
    )
  }

  if (isError) {
    return (
      <div className="bg-dark-card border border-red-500/30 rounded-lg p-8 text-center">
        <AlertTriangle size={32} className="mx-auto mb-3 text-red-400" />
        <p className="text-gray-400">Failed to load learning data</p>
        <button
          onClick={() => refetch()}
          className="mt-3 px-4 py-2 bg-primary-500/20 text-primary-400 rounded-lg text-sm hover:bg-primary-500/30 transition-colors"
        >
          Try Again
        </button>
      </div>
    )
  }

  const stats = analytics || {
    total_journeys: 0,
    completed_journeys: 0,
    total_steps_completed: 0,
    total_hours_spent: 0,
    current_streak: 0,
    longest_streak: 0,
    achievements_earned: 0,
  }

  const achievements = achievementsData?.achievements || []
  const totalPoints = achievementsData?.total_points || 0
  const journeys = activeJourneys?.journeys || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary-500/20 rounded-lg">
            <GraduationCap className="text-primary-400" size={24} />
          </div>
          <div>
            <h2 className="text-lg font-semibold">Learning Dashboard</h2>
            <p className="text-sm text-gray-400">Track your learning progress and achievements</p>
          </div>
        </div>
        <button
          onClick={() => refetch()}
          className="p-2 hover:bg-dark-hover rounded-lg transition-colors"
          title="Refresh"
        >
          <RefreshCw size={18} />
        </button>
      </div>

      {/* Streak & Points Banner */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gradient-to-br from-orange-500/20 to-red-500/20 border border-orange-500/30 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-orange-500/20 rounded-lg">
              <Flame className="text-orange-400" size={24} />
            </div>
            <div>
              <p className="text-2xl font-bold text-orange-400">{stats.current_streak} days</p>
              <p className="text-sm text-gray-400">Current Streak</p>
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-2">Longest: {stats.longest_streak} days</p>
        </div>

        <div className="bg-gradient-to-br from-yellow-500/20 to-amber-500/20 border border-yellow-500/30 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-yellow-500/20 rounded-lg">
              <Trophy className="text-yellow-400" size={24} />
            </div>
            <div>
              <p className="text-2xl font-bold text-yellow-400">{totalPoints}</p>
              <p className="text-sm text-gray-400">Total Points</p>
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-2">{stats.achievements_earned} achievements earned</p>
        </div>

        <div className="bg-gradient-to-br from-green-500/20 to-emerald-500/20 border border-green-500/30 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-green-500/20 rounded-lg">
              <CheckCircle2 className="text-green-400" size={24} />
            </div>
            <div>
              <p className="text-2xl font-bold text-green-400">{stats.completed_journeys}</p>
              <p className="text-sm text-gray-400">Completed Journeys</p>
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-2">{stats.total_steps_completed} steps total</p>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard label="Total Journeys" value={stats.total_journeys} icon={BookOpen} color="text-primary-400" />
        <StatCard label="Steps Completed" value={stats.total_steps_completed} icon={CheckCircle2} color="text-green-400" />
        <StatCard label="Hours Spent" value={stats.total_hours_spent.toFixed(1)} icon={Clock} color="text-blue-400" />
        <StatCard label="Achievements" value={stats.achievements_earned} icon={Award} color="text-yellow-400" />
      </div>

      {/* Active Journeys */}
      {journeys.length > 0 && (
        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <h3 className="font-medium mb-3 flex items-center gap-2">
            <Zap size={16} className="text-primary-400" />
            Active Journeys
          </h3>
          <div className="space-y-3">
            {journeys.slice(0, 3).map((journey) => (
              <JourneyProgressCard key={journey.id} journey={journey} />
            ))}
          </div>
        </div>
      )}

      {/* Recent Achievements */}
      {achievements.length > 0 && (
        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <h3 className="font-medium mb-3 flex items-center gap-2">
            <Trophy size={16} className="text-yellow-400" />
            Achievements
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {achievements.slice(0, 8).map((achievement) => (
              <AchievementBadge key={achievement.id} achievement={achievement} />
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {stats.total_journeys === 0 && (
        <div className="bg-dark-card border border-dark-border rounded-lg p-8 text-center">
          <GraduationCap size={48} className="mx-auto mb-3 text-gray-500" />
          <p className="text-gray-400 mb-2">Start your learning journey!</p>
          <p className="text-sm text-gray-500 mb-4">
            Browse templates to find a learning path that matches your goals
          </p>
        </div>
      )}
    </div>
  )
}

// ============ Journeys Sub-Tab ============

function JourneysSubTab() {
  const [selectedJourney, setSelectedJourney] = useState<LearningJourney | null>(null)
  const [statusFilter, setStatusFilter] = useState<string>('')
  const queryClient = useQueryClient()

  const { data: journeysData, isLoading, isError, refetch } = useQuery({
    queryKey: ['learning-journeys', statusFilter],
    queryFn: async () => {
      let url = '/learning/journeys/'
      if (statusFilter === 'active') url = '/learning/journeys/active/'
      const res = await api.get(url)
      return res.data as { journeys: LearningJourney[]; total: number }
    },
  })

  const pauseMutation = useMutation({
    mutationFn: async (journeyId: string) => {
      const res = await api.post(`/learning/journeys/${journeyId}/pause/`)
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['learning-journeys'] })
    },
  })

  const resumeMutation = useMutation({
    mutationFn: async (journeyId: string) => {
      const res = await api.post(`/learning/journeys/${journeyId}/resume/`)
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['learning-journeys'] })
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="animate-spin text-primary-400" size={24} />
      </div>
    )
  }

  if (isError) {
    return (
      <div className="bg-dark-card border border-red-500/30 rounded-lg p-8 text-center">
        <AlertTriangle size={32} className="mx-auto mb-3 text-red-400" />
        <p className="text-gray-400">Failed to load journeys</p>
        <button
          onClick={() => refetch()}
          className="mt-3 px-4 py-2 bg-primary-500/20 text-primary-400 rounded-lg text-sm hover:bg-primary-500/30 transition-colors"
        >
          Try Again
        </button>
      </div>
    )
  }

  const journeys = journeysData?.journeys || []

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h2 className="text-lg font-semibold">My Learning Journeys</h2>
          <span className="text-sm text-gray-400">({journeysData?.total || 0})</span>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-dark-card border border-dark-border rounded-lg px-3 py-1.5 text-sm"
          >
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="paused">Paused</option>
            <option value="completed">Completed</option>
          </select>
          <button
            onClick={() => refetch()}
            className="p-2 hover:bg-dark-hover rounded-lg transition-colors"
            title="Refresh"
          >
            <RefreshCw size={16} />
          </button>
        </div>
      </div>

      {/* Journeys List */}
      {journeys.length === 0 ? (
        <div className="bg-dark-card border border-dark-border rounded-lg p-8 text-center">
          <BookOpen size={48} className="mx-auto mb-3 text-gray-500" />
          <p className="text-gray-400 mb-2">No journeys found</p>
          <p className="text-sm text-gray-500">
            Start a new journey from the Templates tab
          </p>
        </div>
      ) : (
        <div className="grid gap-4">
          {journeys.map((journey) => (
            <JourneyCard
              key={journey.id}
              journey={journey}
              onSelect={() => setSelectedJourney(journey)}
              onPause={() => pauseMutation.mutate(journey.id)}
              onResume={() => resumeMutation.mutate(journey.id)}
              isPausing={pauseMutation.isPending}
              isResuming={resumeMutation.isPending}
            />
          ))}
        </div>
      )}

      {/* Journey Detail Modal */}
      {selectedJourney && (
        <JourneyDetailModal
          journey={selectedJourney}
          onClose={() => setSelectedJourney(null)}
        />
      )}
    </div>
  )
}

// ============ Templates Sub-Tab ============

function TemplatesSubTab() {
  const [selectedTemplate, setSelectedTemplate] = useState<LearningTemplate | null>(null)
  const [categoryFilter, setCategoryFilter] = useState<string>('')
  const [difficultyFilter, setDifficultyFilter] = useState<string>('')
  const queryClient = useQueryClient()

  const { data: templatesData, isLoading, isError, refetch } = useQuery({
    queryKey: ['learning-templates'],
    queryFn: async () => {
      const res = await api.get('/learning/templates/')
      return res.data as { templates: LearningTemplate[] }
    },
  })

  const startJourneyMutation = useMutation({
    mutationFn: async (templateId: string) => {
      const res = await api.post('/learning/journeys/start/', { template_id: templateId })
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['learning-journeys'] })
      queryClient.invalidateQueries({ queryKey: ['learning-analytics'] })
      setSelectedTemplate(null)
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="animate-spin text-primary-400" size={24} />
      </div>
    )
  }

  if (isError) {
    return (
      <div className="bg-dark-card border border-red-500/30 rounded-lg p-8 text-center">
        <AlertTriangle size={32} className="mx-auto mb-3 text-red-400" />
        <p className="text-gray-400">Failed to load templates</p>
        <button
          onClick={() => refetch()}
          className="mt-3 px-4 py-2 bg-primary-500/20 text-primary-400 rounded-lg text-sm hover:bg-primary-500/30 transition-colors"
        >
          Try Again
        </button>
      </div>
    )
  }

  let templates = templatesData?.templates || []

  // Apply filters
  if (categoryFilter) {
    templates = templates.filter((t) => t.category === categoryFilter)
  }
  if (difficultyFilter) {
    templates = templates.filter((t) => t.difficulty === difficultyFilter)
  }

  const categories = [...new Set(templatesData?.templates.map((t) => t.category) || [])]

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <h2 className="text-lg font-semibold">Learning Templates</h2>
          <span className="text-sm text-gray-400">({templates.length})</span>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="bg-dark-card border border-dark-border rounded-lg px-3 py-1.5 text-sm"
          >
            <option value="">All Categories</option>
            {categories.map((cat) => (
              <option key={cat} value={cat}>
                {cat.replace('_', ' ').replace(/\b\w/g, (c) => c.toUpperCase())}
              </option>
            ))}
          </select>
          <select
            value={difficultyFilter}
            onChange={(e) => setDifficultyFilter(e.target.value)}
            className="bg-dark-card border border-dark-border rounded-lg px-3 py-1.5 text-sm"
          >
            <option value="">All Levels</option>
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
          <button
            onClick={() => refetch()}
            className="p-2 hover:bg-dark-hover rounded-lg transition-colors"
            title="Refresh"
          >
            <RefreshCw size={16} />
          </button>
        </div>
      </div>

      {/* Templates Grid */}
      {templates.length === 0 ? (
        <div className="bg-dark-card border border-dark-border rounded-lg p-8 text-center">
          <Target size={48} className="mx-auto mb-3 text-gray-500" />
          <p className="text-gray-400 mb-2">No templates found</p>
          <p className="text-sm text-gray-500">
            Try adjusting your filters
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {templates.map((template) => (
            <TemplateCard
              key={template.id}
              template={template}
              onSelect={() => setSelectedTemplate(template)}
            />
          ))}
        </div>
      )}

      {/* Template Detail Modal */}
      {selectedTemplate && (
        <TemplateDetailModal
          template={selectedTemplate}
          onClose={() => setSelectedTemplate(null)}
          onStart={() => startJourneyMutation.mutate(selectedTemplate.id)}
          isStarting={startJourneyMutation.isPending}
        />
      )}
    </div>
  )
}

// ============ Helper Components ============

function StatCard({
  label,
  value,
  icon: Icon,
  color,
}: {
  label: string
  value: number | string
  icon: typeof BookOpen
  color: string
}) {
  return (
    <div className="bg-dark-card border border-dark-border rounded-lg p-3">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-400">{label}</p>
          <p className="text-2xl font-bold mt-1">{value}</p>
        </div>
        <div className="p-2 bg-gray-800 rounded-lg">
          <Icon size={20} className={color} />
        </div>
      </div>
    </div>
  )
}

function JourneyProgressCard({ journey }: { journey: LearningJourney }) {
  const statusColors = {
    active: 'text-green-400',
    paused: 'text-yellow-400',
    completed: 'text-blue-400',
    abandoned: 'text-gray-400',
  }

  return (
    <div className="flex items-center gap-4 p-3 bg-dark-bg rounded-lg">
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="font-medium truncate">{journey.title}</span>
          <span className={cn('text-xs capitalize', statusColors[journey.status])}>
            {journey.status}
          </span>
        </div>
        <div className="flex items-center gap-4 text-xs text-gray-500">
          <span>Step {journey.current_step}/{journey.total_steps}</span>
          <span>{journey.progress}% complete</span>
        </div>
      </div>
      <div className="w-24">
        <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-primary-500 transition-all duration-300"
            style={{ width: `${journey.progress}%` }}
          />
        </div>
      </div>
      <ChevronRight size={16} className="text-gray-500" />
    </div>
  )
}

function AchievementBadge({ achievement }: { achievement: Achievement }) {
  const isEarned = !!achievement.earned_at
  const progress = achievement.total > 0 ? (achievement.progress / achievement.total) * 100 : 0

  return (
    <div
      className={cn(
        'p-3 rounded-lg text-center transition-colors',
        isEarned
          ? 'bg-yellow-500/10 border border-yellow-500/30'
          : 'bg-gray-800/50 border border-gray-700 opacity-60'
      )}
    >
      <div className="text-2xl mb-1">{getAchievementIcon(achievement.icon)}</div>
      <p className="text-xs font-medium truncate">{achievement.name}</p>
      {!isEarned && achievement.total > 0 && (
        <div className="mt-2">
          <div className="h-1 bg-gray-700 rounded-full overflow-hidden">
            <div className="h-full bg-yellow-500/50" style={{ width: `${progress}%` }} />
          </div>
          <p className="text-xs text-gray-500 mt-1">
            {achievement.progress}/{achievement.total}
          </p>
        </div>
      )}
    </div>
  )
}

function getAchievementIcon(icon: string): string {
  const icons: Record<string, string> = {
    trophy: '🏆',
    star: '⭐',
    fire: '🔥',
    rocket: '🚀',
    medal: '🥇',
    crown: '👑',
    gem: '💎',
    lightning: '⚡',
    target: '🎯',
    book: '📚',
  }
  return icons[icon] || '🏆'
}

function JourneyCard({
  journey,
  onSelect,
  onPause,
  onResume,
  isPausing,
  isResuming,
}: {
  journey: LearningJourney
  onSelect: () => void
  onPause: () => void
  onResume: () => void
  isPausing: boolean
  isResuming: boolean
}) {
  const statusColors = {
    active: { bg: 'bg-green-500/20', text: 'text-green-400', border: 'border-green-500/30' },
    paused: { bg: 'bg-yellow-500/20', text: 'text-yellow-400', border: 'border-yellow-500/30' },
    completed: { bg: 'bg-blue-500/20', text: 'text-blue-400', border: 'border-blue-500/30' },
    abandoned: { bg: 'bg-gray-500/20', text: 'text-gray-400', border: 'border-gray-500/30' },
  }
  const style = statusColors[journey.status]

  return (
    <div
      className={cn(
        'bg-dark-card border rounded-lg p-4 cursor-pointer hover:border-primary-500/50 transition-colors',
        style.border
      )}
      onClick={onSelect}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold truncate">{journey.title}</h3>
          <p className="text-sm text-gray-400 truncate">{journey.topic}</p>
        </div>
        <span className={cn('text-xs px-2 py-1 rounded capitalize', style.bg, style.text)}>
          {journey.status}
        </span>
      </div>

      <p className="text-sm text-gray-400 line-clamp-2 mb-3">{journey.description}</p>

      <div className="flex items-center gap-4 text-xs text-gray-500 mb-3">
        <span className="flex items-center gap-1">
          <Target size={12} />
          Step {journey.current_step}/{journey.total_steps}
        </span>
        <span className="flex items-center gap-1">
          <Clock size={12} />
          {journey.estimated_hours}h estimated
        </span>
      </div>

      <div className="mb-3">
        <div className="flex items-center justify-between text-xs mb-1">
          <span className="text-gray-400">Progress</span>
          <span className="text-primary-400">{journey.progress}%</span>
        </div>
        <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-primary-500 transition-all duration-300"
            style={{ width: `${journey.progress}%` }}
          />
        </div>
      </div>

      <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
        {journey.status === 'active' && (
          <button
            onClick={onPause}
            disabled={isPausing}
            className="flex items-center gap-1 px-3 py-1.5 text-xs bg-yellow-500/20 text-yellow-400 rounded hover:bg-yellow-500/30 transition-colors disabled:opacity-50"
          >
            {isPausing ? <Loader2 size={12} className="animate-spin" /> : <Pause size={12} />}
            Pause
          </button>
        )}
        {journey.status === 'paused' && (
          <button
            onClick={onResume}
            disabled={isResuming}
            className="flex items-center gap-1 px-3 py-1.5 text-xs bg-green-500/20 text-green-400 rounded hover:bg-green-500/30 transition-colors disabled:opacity-50"
          >
            {isResuming ? <Loader2 size={12} className="animate-spin" /> : <Play size={12} />}
            Resume
          </button>
        )}
      </div>
    </div>
  )
}

function TemplateCard({
  template,
  onSelect,
}: {
  template: LearningTemplate
  onSelect: () => void
}) {
  const difficultyColors = {
    beginner: 'bg-green-500/20 text-green-400',
    intermediate: 'bg-yellow-500/20 text-yellow-400',
    advanced: 'bg-red-500/20 text-red-400',
  }

  return (
    <div
      className="bg-dark-card border border-dark-border rounded-lg p-4 cursor-pointer hover:border-primary-500/50 transition-colors"
      onClick={onSelect}
    >
      <div className="flex items-start justify-between mb-2">
        <h3 className="font-semibold">{template.name}</h3>
        <span className={cn('text-xs px-2 py-0.5 rounded capitalize', difficultyColors[template.difficulty])}>
          {template.difficulty}
        </span>
      </div>

      <p className="text-sm text-gray-400 line-clamp-2 mb-3">{template.description}</p>

      <div className="flex items-center gap-3 text-xs text-gray-500 mb-3">
        <span className="flex items-center gap-1">
          <Target size={12} />
          {template.steps_count} steps
        </span>
        <span className="flex items-center gap-1">
          <Clock size={12} />
          {template.estimated_hours}h
        </span>
        <span className="flex items-center gap-1">
          <Star size={12} />
          {template.popularity}
        </span>
      </div>

      <div className="flex flex-wrap gap-1">
        {template.tags.slice(0, 3).map((tag) => (
          <span key={tag} className="text-xs px-2 py-0.5 bg-gray-800 rounded text-gray-400">
            {tag}
          </span>
        ))}
        {template.tags.length > 3 && (
          <span className="text-xs px-2 py-0.5 bg-gray-800 rounded text-gray-400">
            +{template.tags.length - 3}
          </span>
        )}
      </div>
    </div>
  )
}

// ============ Modals ============

function JourneyDetailModal({
  journey,
  onClose,
}: {
  journey: LearningJourney
  onClose: () => void
}) {
  const queryClient = useQueryClient()

  const completeStepMutation = useMutation({
    mutationFn: async (stepNumber: number) => {
      const res = await api.post(
        `/learning/journeys/${journey.id}/step/${stepNumber}/complete/`
      )
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['learning-journeys'] })
      queryClient.invalidateQueries({ queryKey: ['learning-analytics'] })
    },
  })

  const startStepMutation = useMutation({
    mutationFn: async (stepNumber: number) => {
      const res = await api.post(
        `/learning/journeys/${journey.id}/step/${stepNumber}/start/`
      )
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['learning-journeys'] })
    },
  })

  const statusColors = {
    pending: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
    in_progress: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
    completed: 'bg-green-500/20 text-green-400 border-green-500/30',
    skipped: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30',
  }

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={onClose}>
      <div
        className="bg-dark-card border border-dark-border rounded-xl w-full max-w-2xl mx-4 max-h-[85vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-dark-border">
          <div>
            <h3 className="font-semibold text-lg">{journey.title}</h3>
            <p className="text-sm text-gray-400">{journey.topic}</p>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-gray-700 rounded transition-colors">
            <X size={20} className="text-gray-400" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* Progress */}
          <div className="bg-dark-bg rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-400">Overall Progress</span>
              <span className="text-lg font-bold text-primary-400">{journey.progress}%</span>
            </div>
            <div className="h-3 bg-gray-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-primary-500 to-primary-400 transition-all duration-300"
                style={{ width: `${journey.progress}%` }}
              />
            </div>
          </div>

          {/* Goals */}
          {journey.goals.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-gray-400 mb-2">Goals</h4>
              <ul className="space-y-1">
                {journey.goals.map((goal, i) => (
                  <li key={i} className="flex items-center gap-2 text-sm">
                    <Target size={12} className="text-primary-400" />
                    {goal}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Steps */}
          <div>
            <h4 className="text-sm font-medium text-gray-400 mb-3">Steps</h4>
            <div className="space-y-2">
              {journey.steps.map((step) => (
                <div
                  key={step.step_number}
                  className={cn(
                    'border rounded-lg p-3',
                    statusColors[step.status]
                  )}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-medium px-2 py-0.5 bg-gray-800 rounded">
                        Step {step.step_number}
                      </span>
                      <span className="font-medium">{step.title}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      {step.status === 'pending' && (
                        <button
                          onClick={() => startStepMutation.mutate(step.step_number)}
                          disabled={startStepMutation.isPending}
                          className="flex items-center gap-1 px-2 py-1 text-xs bg-blue-500/20 text-blue-400 rounded hover:bg-blue-500/30 transition-colors"
                        >
                          <Play size={10} />
                          Start
                        </button>
                      )}
                      {step.status === 'in_progress' && (
                        <button
                          onClick={() => completeStepMutation.mutate(step.step_number)}
                          disabled={completeStepMutation.isPending}
                          className="flex items-center gap-1 px-2 py-1 text-xs bg-green-500/20 text-green-400 rounded hover:bg-green-500/30 transition-colors"
                        >
                          <CheckCircle2 size={10} />
                          Complete
                        </button>
                      )}
                      {step.status === 'completed' && (
                        <CheckCircle2 size={16} className="text-green-400" />
                      )}
                    </div>
                  </div>
                  {step.description && (
                    <p className="text-xs text-gray-400 mt-2">{step.description}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-dark-border flex justify-end">
          <button onClick={onClose} className="px-4 py-2 bg-primary-500/20 text-primary-400 rounded-lg text-sm hover:bg-primary-500/30 transition-colors">
            Close
          </button>
        </div>
      </div>
    </div>
  )
}

function TemplateDetailModal({
  template,
  onClose,
  onStart,
  isStarting,
}: {
  template: LearningTemplate
  onClose: () => void
  onStart: () => void
  isStarting: boolean
}) {
  const difficultyColors = {
    beginner: 'bg-green-500/20 text-green-400',
    intermediate: 'bg-yellow-500/20 text-yellow-400',
    advanced: 'bg-red-500/20 text-red-400',
  }

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={onClose}>
      <div
        className="bg-dark-card border border-dark-border rounded-xl w-full max-w-lg mx-4 max-h-[85vh] overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-dark-border">
          <div>
            <h3 className="font-semibold text-lg">{template.name}</h3>
            <div className="flex items-center gap-2 mt-1">
              <span className={cn('text-xs px-2 py-0.5 rounded capitalize', difficultyColors[template.difficulty])}>
                {template.difficulty}
              </span>
              <span className="text-xs text-gray-400">
                {template.category.replace('_', ' ')}
              </span>
            </div>
          </div>
          <button onClick={onClose} className="p-1 hover:bg-gray-700 rounded transition-colors">
            <X size={20} className="text-gray-400" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          <p className="text-gray-300">{template.description}</p>

          <div className="grid grid-cols-3 gap-3">
            <div className="bg-dark-bg rounded-lg p-3 text-center">
              <Target size={20} className="mx-auto mb-1 text-primary-400" />
              <p className="text-lg font-bold">{template.steps_count}</p>
              <p className="text-xs text-gray-400">Steps</p>
            </div>
            <div className="bg-dark-bg rounded-lg p-3 text-center">
              <Clock size={20} className="mx-auto mb-1 text-blue-400" />
              <p className="text-lg font-bold">{template.estimated_hours}</p>
              <p className="text-xs text-gray-400">Hours</p>
            </div>
            <div className="bg-dark-bg rounded-lg p-3 text-center">
              <Star size={20} className="mx-auto mb-1 text-yellow-400" />
              <p className="text-lg font-bold">{template.popularity}</p>
              <p className="text-xs text-gray-400">Started</p>
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            {template.tags.map((tag) => (
              <span key={tag} className="text-xs px-2 py-1 bg-gray-800 rounded text-gray-400">
                {tag}
              </span>
            ))}
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-dark-border flex justify-end gap-2">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-400 hover:text-white transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onStart}
            disabled={isStarting}
            className="flex items-center gap-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors disabled:opacity-50"
          >
            {isStarting ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <Plus size={16} />
            )}
            Start Journey
          </button>
        </div>
      </div>
    </div>
  )
}

// ============ Session 956: AI Learning Effectiveness Sub-Tab ============

function EffectivenessSubTab() {
  const queryClient = useQueryClient()

  // Fetch learning loop stats
  const { data: stats, isLoading, isError, refetch } = useQuery({
    queryKey: ['learning-loop-stats'],
    queryFn: async () => {
      const res = await api.get('/learning/loop/stats/')
      return res.data as LearningLoopStats
    },
    refetchInterval: 60000, // Refresh every minute
  })

  // Track learning outcome mutation
  const trackMutation = useMutation({
    mutationFn: async ({ patternId, wasSuccessful }: { patternId: string; wasSuccessful: boolean }) => {
      const res = await api.post('/learning/loop/track/', {
        pattern_id: patternId,
        was_successful: wasSuccessful,
      })
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['learning-loop-stats'] })
    },
  })

  // Run learning cycle mutation
  const runCycleMutation = useMutation({
    mutationFn: async () => {
      const res = await api.post('/learning/loop/run/')
      return res.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['learning-loop-stats'] })
    },
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="animate-spin text-primary-400" size={24} />
      </div>
    )
  }

  if (isError) {
    return (
      <div className="bg-dark-card border border-red-500/30 rounded-lg p-8 text-center">
        <AlertTriangle size={32} className="mx-auto mb-3 text-red-400" />
        <p className="text-gray-400">Failed to load AI learning data</p>
        <button
          onClick={() => refetch()}
          className="mt-3 px-4 py-2 bg-primary-500/20 text-primary-400 rounded-lg text-sm hover:bg-primary-500/30 transition-colors"
        >
          Try Again
        </button>
      </div>
    )
  }

  const effectivenessPercent = Math.round((stats?.overall_effectiveness ?? 0) * 100)
  const mostEffective = stats?.most_effective ?? []
  const leastEffective = stats?.least_effective ?? []
  const recentLearnings = stats?.recent_learnings ?? []
  const byPatternType = stats?.by_pattern_type ?? []

  const getEffectivenessColor = (rate: number) => {
    if (rate >= 0.7) return 'text-green-400'
    if (rate >= 0.4) return 'text-amber-400'
    return 'text-red-400'
  }

  const getEffectivenessBarColor = (rate: number) => {
    if (rate >= 0.7) return 'bg-green-500'
    if (rate >= 0.4) return 'bg-amber-500'
    return 'bg-red-500'
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary-500/20 rounded-lg">
            <Brain className="text-primary-400" size={24} />
          </div>
          <div>
            <h2 className="text-lg font-semibold">AI Learning Effectiveness</h2>
            <p className="text-sm text-gray-400">Track how well the AI learns from your decisions</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => runCycleMutation.mutate()}
            disabled={runCycleMutation.isPending}
            className="flex items-center gap-2 px-3 py-2 bg-primary-500/20 text-primary-400 rounded-lg text-sm hover:bg-primary-500/30 transition-colors disabled:opacity-50"
            title="Run learning cycle"
          >
            {runCycleMutation.isPending ? (
              <Loader2 size={14} className="animate-spin" />
            ) : (
              <Sparkles size={14} />
            )}
            Run Cycle
          </button>
          <button
            onClick={() => refetch()}
            className="p-2 hover:bg-dark-hover rounded-lg transition-colors"
            title="Refresh"
          >
            <RefreshCw size={18} />
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Activity size={16} className="text-primary-400" />
            <span className="text-xs text-gray-400">Active Learnings</span>
          </div>
          <p className="text-2xl font-bold">{stats?.total_active_learnings ?? 0}</p>
        </div>

        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <BarChart3 size={16} className="text-blue-400" />
            <span className="text-xs text-gray-400">Times Applied</span>
          </div>
          <p className="text-2xl font-bold">{stats?.total_applied ?? 0}</p>
        </div>

        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <CheckCircle2 size={16} className="text-green-400" />
            <span className="text-xs text-gray-400">Successful</span>
          </div>
          <p className="text-2xl font-bold text-green-400">{stats?.total_successful ?? 0}</p>
        </div>

        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp size={16} className={getEffectivenessColor(stats?.overall_effectiveness ?? 0)} />
            <span className="text-xs text-gray-400">Effectiveness</span>
          </div>
          <p className={cn("text-2xl font-bold", getEffectivenessColor(stats?.overall_effectiveness ?? 0))}>
            {effectivenessPercent}%
          </p>
        </div>
      </div>

      {/* Most & Least Effective Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Most Effective */}
        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <h3 className="flex items-center gap-2 font-medium mb-4">
            <ThumbsUp size={16} className="text-green-400" />
            Most Effective Patterns
          </h3>
          {mostEffective.length === 0 ? (
            <p className="text-sm text-gray-500 text-center py-4">No patterns applied yet</p>
          ) : (
            <div className="space-y-3">
              {mostEffective.slice(0, 5).map((pattern) => (
                <div key={pattern.id} className="space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-300 truncate flex-1 mr-2" title={pattern.description}>
                      {pattern.description.length > 60 ? `${pattern.description.slice(0, 60)}...` : pattern.description}
                    </span>
                    <span className={cn("text-xs font-medium", getEffectivenessColor(pattern.effectiveness))}>
                      {Math.round(pattern.effectiveness * 100)}%
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-1.5 bg-dark-border rounded-full overflow-hidden">
                      <div
                        className={cn("h-full rounded-full", getEffectivenessBarColor(pattern.effectiveness))}
                        style={{ width: `${pattern.effectiveness * 100}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-500 w-16 text-right">{pattern.times_applied}× used</span>
                  </div>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs px-1.5 py-0.5 bg-dark-border rounded text-gray-400">
                      {pattern.pattern_type}
                    </span>
                    <button
                      onClick={() => trackMutation.mutate({ patternId: pattern.id, wasSuccessful: true })}
                      disabled={trackMutation.isPending}
                      className="text-xs text-gray-500 hover:text-green-400 transition-colors"
                      title="Mark as helpful"
                    >
                      <ThumbsUp size={12} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Least Effective */}
        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <h3 className="flex items-center gap-2 font-medium mb-4">
            <ThumbsDown size={16} className="text-red-400" />
            Needs Improvement
          </h3>
          {leastEffective.length === 0 ? (
            <p className="text-sm text-gray-500 text-center py-4">All patterns performing well!</p>
          ) : (
            <div className="space-y-3">
              {leastEffective.slice(0, 5).map((pattern) => (
                <div key={pattern.id} className="space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-300 truncate flex-1 mr-2" title={pattern.description}>
                      {pattern.description.length > 60 ? `${pattern.description.slice(0, 60)}...` : pattern.description}
                    </span>
                    <span className={cn("text-xs font-medium", getEffectivenessColor(pattern.effectiveness))}>
                      {Math.round(pattern.effectiveness * 100)}%
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-1.5 bg-dark-border rounded-full overflow-hidden">
                      <div
                        className={cn("h-full rounded-full", getEffectivenessBarColor(pattern.effectiveness))}
                        style={{ width: `${pattern.effectiveness * 100}%` }}
                      />
                    </div>
                    <span className="text-xs text-gray-500 w-16 text-right">{pattern.times_applied}× used</span>
                  </div>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs px-1.5 py-0.5 bg-dark-border rounded text-gray-400">
                      {pattern.pattern_type}
                    </span>
                    <button
                      onClick={() => trackMutation.mutate({ patternId: pattern.id, wasSuccessful: false })}
                      disabled={trackMutation.isPending}
                      className="text-xs text-gray-500 hover:text-red-400 transition-colors"
                      title="Mark as not helpful"
                    >
                      <ThumbsDown size={12} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Pattern Type Breakdown & Recent Learnings */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* By Pattern Type */}
        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <h3 className="flex items-center gap-2 font-medium mb-4">
            <BarChart3 size={16} className="text-primary-400" />
            By Pattern Type
          </h3>
          {byPatternType.length === 0 ? (
            <p className="text-sm text-gray-500 text-center py-4">No patterns yet</p>
          ) : (
            <div className="space-y-3">
              {byPatternType.map((type) => (
                <div key={type.pattern_type} className="flex items-center justify-between">
                  <div className="flex items-center gap-2 flex-1">
                    <span className="text-sm text-gray-300 capitalize">
                      {type.pattern_type.replace(/_/g, ' ')}
                    </span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xs text-gray-500">{type.count} patterns</span>
                    <span className="text-xs text-primary-400">{Math.round(type.avg_confidence * 100)}% conf</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent Learnings */}
        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <h3 className="flex items-center gap-2 font-medium mb-4">
            <Clock size={16} className="text-amber-400" />
            Recent Learnings
          </h3>
          {recentLearnings.length === 0 ? (
            <p className="text-sm text-gray-500 text-center py-4">No recent learnings</p>
          ) : (
            <div className="space-y-3 max-h-[300px] overflow-y-auto">
              {recentLearnings.slice(0, 10).map((learning) => (
                <div key={learning.id} className="p-2 bg-dark-bg/50 rounded">
                  <p className="text-sm text-gray-300 line-clamp-2" title={learning.description}>
                    {learning.description}
                  </p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs px-1.5 py-0.5 bg-dark-border rounded text-gray-400">
                      {learning.pattern_type}
                    </span>
                    {learning.confidence && (
                      <span className="text-xs text-gray-500">
                        {Math.round(learning.confidence * 100)}% confidence
                      </span>
                    )}
                    {learning.created_at && (
                      <span className="text-xs text-gray-600 ml-auto">
                        {new Date(learning.created_at).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Last Updated */}
      {stats?.timestamp && (
        <p className="text-xs text-gray-600 text-center">
          Last updated: {new Date(stats.timestamp).toLocaleString()}
        </p>
      )}
    </div>
  )
}
