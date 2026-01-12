import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { journeyApi } from '@/lib/api'
import { cn } from '@/lib/cn'
import {
  GraduationCap,
  Play,
  Pause,
  CheckCircle,
  Circle,
  Clock,
  Target,
  Trophy,
  BookOpen,
  ChevronDown,
  ChevronUp,
  Loader2,
  Plus,
  SkipForward,
  Award,
  TrendingUp,
  Calendar,
  Star,
} from 'lucide-react'

// Types
interface JourneyStep {
  step_number: number
  title: string
  description?: string
  status: 'pending' | 'in_progress' | 'completed' | 'skipped'
  started_at?: string
  completed_at?: string
  duration_minutes?: number
  notes?: string
}

interface Journey {
  id: string
  title: string
  description?: string
  topic?: string
  status: 'active' | 'paused' | 'completed' | 'abandoned'
  progress: number
  current_step: number
  total_steps: number
  steps?: JourneyStep[]
  started_at?: string
  completed_at?: string
  estimated_hours?: number
  goals?: string[]
}

interface JourneyTemplate {
  id: string
  name: string
  description?: string
  category?: string
  difficulty?: 'beginner' | 'intermediate' | 'advanced'
  estimated_hours?: number
  steps_count?: number
  popularity?: number
  tags?: string[]
}

interface Achievement {
  id: string
  name: string
  description?: string
  icon?: string
  earned_at?: string
  progress?: number
  total?: number
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

type TabType = 'active' | 'templates' | 'completed' | 'achievements'

export default function LearningJourneyPage() {
  const [activeTab, setActiveTab] = useState<TabType>('active')
  const [expandedJourney, setExpandedJourney] = useState<string | null>(null)
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null)
  const queryClient = useQueryClient()

  // Queries
  const { data: activeJourneysData, isLoading: loadingActive } = useQuery({
    queryKey: ['journeys-active'],
    queryFn: () => journeyApi.active(),
    enabled: activeTab === 'active',
  })

  const { data: allJourneysData, isLoading: loadingAll } = useQuery({
    queryKey: ['journeys-all'],
    queryFn: () => journeyApi.list(),
    enabled: activeTab === 'completed',
  })

  const { data: templatesData, isLoading: loadingTemplates } = useQuery({
    queryKey: ['journey-templates'],
    queryFn: () => journeyApi.templates(),
    enabled: activeTab === 'templates',
  })

  const { data: achievementsData, isLoading: loadingAchievements } = useQuery({
    queryKey: ['journey-achievements'],
    queryFn: () => journeyApi.achievements(),
    enabled: activeTab === 'achievements',
  })

  const { data: analyticsData } = useQuery({
    queryKey: ['journey-analytics'],
    queryFn: () => journeyApi.analytics(),
  })

  // Mutations
  const startJourney = useMutation({
    mutationFn: (templateId: string) => journeyApi.start({ template_id: templateId }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['journeys-active'] })
      setSelectedTemplate(null)
      setActiveTab('active')
    },
  })

  const pauseJourney = useMutation({
    mutationFn: (id: string) => journeyApi.pause(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['journeys-active'] })
    },
  })

  const resumeJourney = useMutation({
    mutationFn: (id: string) => journeyApi.resume(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['journeys-active'] })
    },
  })

  const startStep = useMutation({
    mutationFn: ({ journeyId, step }: { journeyId: string; step: number }) =>
      journeyApi.startStep(journeyId, step),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['journeys-active'] })
    },
  })

  const completeStep = useMutation({
    mutationFn: ({ journeyId, step }: { journeyId: string; step: number }) =>
      journeyApi.completeStep(journeyId, step),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['journeys-active'] })
    },
  })

  const skipStep = useMutation({
    mutationFn: ({ journeyId, step }: { journeyId: string; step: number }) =>
      journeyApi.skipStep(journeyId, step),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['journeys-active'] })
    },
  })

  // Data extraction
  const rawActive = activeJourneysData?.data?.journeys || activeJourneysData?.data?.results || activeJourneysData?.data
  const activeJourneys: Journey[] = Array.isArray(rawActive) ? rawActive : []
  const rawAll = allJourneysData?.data?.journeys || allJourneysData?.data?.results || allJourneysData?.data
  const allJourneys: Journey[] = Array.isArray(rawAll) ? rawAll : []
  const completedJourneys = allJourneys.filter(j => j.status === 'completed')
  const rawTemplates = templatesData?.data?.templates || templatesData?.data?.results || templatesData?.data
  const templates: JourneyTemplate[] = Array.isArray(rawTemplates) ? rawTemplates : []
  const rawAchievements = achievementsData?.data?.achievements || achievementsData?.data?.results || achievementsData?.data
  const achievements: Achievement[] = Array.isArray(rawAchievements) ? rawAchievements : []
  const analytics: Analytics = analyticsData?.data || {}

  const tabs = [
    { id: 'active' as TabType, label: 'Active', icon: Play, badge: activeJourneys.length },
    { id: 'templates' as TabType, label: 'Start New', icon: Plus },
    { id: 'completed' as TabType, label: 'Completed', icon: CheckCircle },
    { id: 'achievements' as TabType, label: 'Achievements', icon: Trophy, badge: achievements.length },
  ]

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '—'
    return new Date(dateStr).toLocaleDateString()
  }

  const getDifficultyColor = (difficulty?: string) => {
    switch (difficulty) {
      case 'beginner':
        return 'text-accent-green bg-accent-green/20'
      case 'intermediate':
        return 'text-yellow-400 bg-yellow-500/20'
      case 'advanced':
        return 'text-red-400 bg-red-500/20'
      default:
        return 'text-gray-400 bg-gray-500/20'
    }
  }

  const getStepStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-accent-green" />
      case 'in_progress':
        return <Play className="h-5 w-5 text-primary-400" />
      case 'skipped':
        return <SkipForward className="h-5 w-5 text-gray-500" />
      default:
        return <Circle className="h-5 w-5 text-gray-600" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-indigo-500/20">
            <GraduationCap className="h-6 w-6 text-indigo-400" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">Learning Journeys</h1>
            <p className="text-gray-400">Guided learning paths to master new skills</p>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="flex items-center gap-6">
          <div className="text-center">
            <p className="text-2xl font-bold">{analytics.completed_journeys || 0}</p>
            <p className="text-xs text-gray-500">Completed</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-accent-green">{analytics.current_streak || 0}</p>
            <p className="text-xs text-gray-500">Day Streak</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-yellow-400">{analytics.achievements_earned || 0}</p>
            <p className="text-xs text-gray-500">Achievements</p>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-dark-border pb-2">
        {tabs.map((tab) => {
          const Icon = tab.icon
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                'flex items-center gap-2 px-4 py-2 rounded-t-lg transition-colors',
                activeTab === tab.id
                  ? 'bg-dark-card text-white border-b-2 border-primary-500'
                  : 'text-gray-400 hover:text-white hover:bg-dark-card/50'
              )}
            >
              <Icon className="h-4 w-4" />
              <span>{tab.label}</span>
              {tab.badge !== undefined && tab.badge > 0 && (
                <span className="ml-1 px-1.5 py-0.5 text-xs rounded-full bg-primary-600">
                  {tab.badge}
                </span>
              )}
            </button>
          )
        })}
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {/* Active Journeys Tab */}
        {activeTab === 'active' && (
          <div className="space-y-4">
            {loadingActive ? (
              <div className="flex justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
              </div>
            ) : activeJourneys.length === 0 ? (
              <div className="text-center py-12">
                <BookOpen className="h-12 w-12 text-gray-600 mx-auto mb-3" />
                <p className="text-gray-400">No active learning journeys</p>
                <p className="text-sm text-gray-500 mb-4">Start a new journey to begin learning</p>
                <button
                  onClick={() => setActiveTab('templates')}
                  className="btn-primary"
                >
                  Browse Templates
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                {activeJourneys.map((journey) => (
                  <div key={journey.id} className="card overflow-hidden">
                    {/* Journey Header */}
                    <div
                      className="p-4 cursor-pointer hover:bg-dark-bg/50"
                      onClick={() => setExpandedJourney(
                        expandedJourney === journey.id ? null : journey.id
                      )}
                    >
                      <div className="flex items-center gap-4">
                        <div className="p-3 rounded-lg bg-indigo-500/20">
                          <Target className="h-6 w-6 text-indigo-400" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <h3 className="font-semibold">{journey.title}</h3>
                            <span className={cn(
                              'px-2 py-0.5 text-xs rounded capitalize',
                              journey.status === 'active' ? 'bg-accent-green/20 text-accent-green' :
                              journey.status === 'paused' ? 'bg-yellow-500/20 text-yellow-400' :
                              'bg-gray-500/20 text-gray-400'
                            )}>
                              {journey.status}
                            </span>
                          </div>
                          <p className="text-sm text-gray-400">
                            Step {journey.current_step} of {journey.total_steps} • {journey.progress}% complete
                          </p>
                        </div>
                        <div className="flex items-center gap-3">
                          {journey.status === 'active' ? (
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                pauseJourney.mutate(journey.id)
                              }}
                              disabled={pauseJourney.isPending}
                              className="p-2 rounded hover:bg-dark-bg text-yellow-400"
                              title="Pause"
                            >
                              <Pause className="h-5 w-5" />
                            </button>
                          ) : (
                            <button
                              onClick={(e) => {
                                e.stopPropagation()
                                resumeJourney.mutate(journey.id)
                              }}
                              disabled={resumeJourney.isPending}
                              className="p-2 rounded hover:bg-dark-bg text-accent-green"
                              title="Resume"
                            >
                              <Play className="h-5 w-5" />
                            </button>
                          )}
                          {expandedJourney === journey.id ? (
                            <ChevronUp className="h-5 w-5 text-gray-400" />
                          ) : (
                            <ChevronDown className="h-5 w-5 text-gray-400" />
                          )}
                        </div>
                      </div>

                      {/* Progress Bar */}
                      <div className="mt-3 h-2 bg-dark-bg rounded-full overflow-hidden">
                        <div
                          className="h-full bg-indigo-500 rounded-full transition-all"
                          style={{ width: `${journey.progress}%` }}
                        />
                      </div>
                    </div>

                    {/* Expanded Steps */}
                    {expandedJourney === journey.id && journey.steps && (
                      <div className="border-t border-dark-border p-4 bg-dark-bg/30">
                        <div className="space-y-3">
                          {journey.steps.map((step) => (
                            <div
                              key={step.step_number}
                              className={cn(
                                'flex items-center gap-3 p-3 rounded-lg',
                                step.status === 'in_progress' && 'bg-primary-500/10 border border-primary-500/30'
                              )}
                            >
                              {getStepStatusIcon(step.status)}
                              <div className="flex-1 min-w-0">
                                <p className={cn(
                                  'font-medium',
                                  step.status === 'completed' && 'text-gray-500 line-through',
                                  step.status === 'skipped' && 'text-gray-500'
                                )}>
                                  {step.step_number}. {step.title}
                                </p>
                                {step.description && (
                                  <p className="text-sm text-gray-500">{step.description}</p>
                                )}
                              </div>
                              {step.status === 'pending' && (
                                <div className="flex items-center gap-1">
                                  <button
                                    onClick={() => startStep.mutate({ journeyId: journey.id, step: step.step_number })}
                                    disabled={startStep.isPending}
                                    className="px-3 py-1 text-sm rounded bg-primary-600 hover:bg-primary-700"
                                  >
                                    Start
                                  </button>
                                  <button
                                    onClick={() => skipStep.mutate({ journeyId: journey.id, step: step.step_number })}
                                    disabled={skipStep.isPending}
                                    className="p-1.5 rounded hover:bg-dark-bg text-gray-500"
                                    title="Skip"
                                  >
                                    <SkipForward className="h-4 w-4" />
                                  </button>
                                </div>
                              )}
                              {step.status === 'in_progress' && (
                                <button
                                  onClick={() => completeStep.mutate({ journeyId: journey.id, step: step.step_number })}
                                  disabled={completeStep.isPending}
                                  className="px-3 py-1 text-sm rounded bg-accent-green hover:bg-accent-green/80 text-black"
                                >
                                  Complete
                                </button>
                              )}
                              {step.completed_at && (
                                <span className="text-xs text-gray-500">
                                  {formatDate(step.completed_at)}
                                </span>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Templates Tab */}
        {activeTab === 'templates' && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold">Choose a Learning Path</h2>

            {loadingTemplates ? (
              <div className="flex justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
              </div>
            ) : templates.length === 0 ? (
              <div className="text-center py-12">
                <BookOpen className="h-12 w-12 text-gray-600 mx-auto mb-3" />
                <p className="text-gray-400">No templates available</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {templates.map((template) => (
                  <div
                    key={template.id}
                    className={cn(
                      'card p-5 cursor-pointer transition-all hover:border-primary-500/50',
                      selectedTemplate === template.id && 'border-primary-500'
                    )}
                    onClick={() => setSelectedTemplate(
                      selectedTemplate === template.id ? null : template.id
                    )}
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="p-2 rounded-lg bg-indigo-500/20">
                        <BookOpen className="h-5 w-5 text-indigo-400" />
                      </div>
                      {template.difficulty && (
                        <span className={cn(
                          'px-2 py-0.5 text-xs rounded capitalize',
                          getDifficultyColor(template.difficulty)
                        )}>
                          {template.difficulty}
                        </span>
                      )}
                    </div>

                    <h3 className="font-semibold mb-1">{template.name}</h3>
                    {template.description && (
                      <p className="text-sm text-gray-400 mb-3 line-clamp-2">{template.description}</p>
                    )}

                    <div className="flex items-center gap-4 text-sm text-gray-500 mb-3">
                      {template.steps_count && (
                        <span className="flex items-center gap-1">
                          <Target className="h-4 w-4" />
                          {template.steps_count} steps
                        </span>
                      )}
                      {template.estimated_hours && (
                        <span className="flex items-center gap-1">
                          <Clock className="h-4 w-4" />
                          {template.estimated_hours}h
                        </span>
                      )}
                    </div>

                    {template.tags && template.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1 mb-3">
                        {template.tags.slice(0, 3).map((tag) => (
                          <span key={tag} className="px-2 py-0.5 text-xs rounded bg-dark-bg text-gray-400">
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}

                    {selectedTemplate === template.id && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          startJourney.mutate(template.id)
                        }}
                        disabled={startJourney.isPending}
                        className="w-full mt-2 btn-primary flex items-center justify-center gap-2"
                      >
                        {startJourney.isPending ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <>
                            <Play className="h-4 w-4" />
                            Start Journey
                          </>
                        )}
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Completed Tab */}
        {activeTab === 'completed' && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold">Completed Journeys</h2>

            {loadingAll ? (
              <div className="flex justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
              </div>
            ) : completedJourneys.length === 0 ? (
              <div className="text-center py-12">
                <Trophy className="h-12 w-12 text-gray-600 mx-auto mb-3" />
                <p className="text-gray-400">No completed journeys yet</p>
                <p className="text-sm text-gray-500">Complete your first journey to see it here</p>
              </div>
            ) : (
              <div className="space-y-3">
                {completedJourneys.map((journey) => (
                  <div key={journey.id} className="card p-4 flex items-center gap-4">
                    <div className="p-3 rounded-lg bg-accent-green/20">
                      <CheckCircle className="h-6 w-6 text-accent-green" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium">{journey.title}</h3>
                      <p className="text-sm text-gray-400">
                        {journey.total_steps} steps • Completed {formatDate(journey.completed_at)}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Star className="h-5 w-5 text-yellow-400 fill-yellow-400" />
                      <span className="text-sm text-gray-400">100%</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Achievements Tab */}
        {activeTab === 'achievements' && (
          <div className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="card p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-indigo-500/20">
                    <TrendingUp className="h-5 w-5 text-indigo-400" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Total Steps</p>
                    <p className="text-xl font-bold">{analytics.total_steps_completed || 0}</p>
                  </div>
                </div>
              </div>

              <div className="card p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-accent-green/20">
                    <Clock className="h-5 w-5 text-accent-green" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Hours Spent</p>
                    <p className="text-xl font-bold">{analytics.total_hours_spent || 0}</p>
                  </div>
                </div>
              </div>

              <div className="card p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-yellow-500/20">
                    <Calendar className="h-5 w-5 text-yellow-400" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Current Streak</p>
                    <p className="text-xl font-bold">{analytics.current_streak || 0} days</p>
                  </div>
                </div>
              </div>

              <div className="card p-4">
                <div className="flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-purple-500/20">
                    <Award className="h-5 w-5 text-purple-400" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Longest Streak</p>
                    <p className="text-xl font-bold">{analytics.longest_streak || 0} days</p>
                  </div>
                </div>
              </div>
            </div>

            <h2 className="text-lg font-semibold">Your Achievements</h2>

            {loadingAchievements ? (
              <div className="flex justify-center py-12">
                <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
              </div>
            ) : achievements.length === 0 ? (
              <div className="text-center py-12">
                <Trophy className="h-12 w-12 text-gray-600 mx-auto mb-3" />
                <p className="text-gray-400">No achievements earned yet</p>
                <p className="text-sm text-gray-500">Complete learning journeys to earn achievements</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {achievements.map((achievement) => (
                  <div key={achievement.id} className="card p-4 flex items-center gap-4">
                    <div className="p-3 rounded-lg bg-yellow-500/20">
                      <Trophy className="h-6 w-6 text-yellow-400" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium">{achievement.name}</h3>
                      {achievement.description && (
                        <p className="text-sm text-gray-400">{achievement.description}</p>
                      )}
                      {achievement.earned_at && (
                        <p className="text-xs text-gray-500 mt-1">
                          Earned {formatDate(achievement.earned_at)}
                        </p>
                      )}
                    </div>
                    {achievement.progress !== undefined && achievement.total && (
                      <div className="text-right">
                        <p className="text-sm font-medium">
                          {achievement.progress}/{achievement.total}
                        </p>
                        <div className="w-16 h-1.5 bg-dark-bg rounded-full overflow-hidden mt-1">
                          <div
                            className="h-full bg-yellow-500 rounded-full"
                            style={{ width: `${(achievement.progress / achievement.total) * 100}%` }}
                          />
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
