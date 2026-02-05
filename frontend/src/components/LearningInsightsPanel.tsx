/**
 * Session 935: Learning Insights Panel Component
 *
 * Displays user learning summary including:
 * - Profile completeness
 * - Agent effectiveness
 * - Skill progress
 * - Learning recommendations
 */

import { useQuery } from '@tanstack/react-query'
import {
  Brain,
  Sparkles,
  TrendingUp,
  Target,
  User,
  Lightbulb,
  BarChart3,
  ChevronRight,
  Loader2,
  Star,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { userLearningApi } from '@/lib/api'

interface ProfileStats {
  completion_percentage: number
  total_fields: number
  completed_fields: number
  missing_fields: string[]
  priority_field?: string
}

interface AgentSummary {
  total_agents_used: number
  total_feedbacks: number
  top_agents: Array<{
    agent_id: string
    agent_name: string
    effectiveness_score: number
    total_feedbacks: number
  }>
  recent_trend: 'improving' | 'stable' | 'declining'
}

interface SkillsSummary {
  total_skills: number
  skill_categories: Record<string, number>
  top_skills: Array<{
    name: string
    level: number
    category: string
    recent_growth: number
  }>
  learning_velocity: number
}

interface GoalsSummary {
  total_goals: number
  active_goals: number
  completed_goals: number
  overall_progress: number
}

interface LearningSummary {
  profile: ProfileStats
  agents: AgentSummary
  skills: SkillsSummary
  goals: GoalsSummary
}

interface LearningInsightsPanelProps {
  /** Compact mode for sidebar */
  compact?: boolean
  /** Additional classes */
  className?: string
}

export function LearningInsightsPanel({
  compact = false,
  className,
}: LearningInsightsPanelProps) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['user-learning-summary'],
    queryFn: async () => {
      const response = await userLearningApi.getSummary()
      return response.data as { success: boolean; data: LearningSummary }
    },
    refetchInterval: 120000, // Refresh every 2 minutes
  })

  const summary = data?.data

  if (isLoading) {
    return (
      <div className={cn('flex items-center justify-center p-4', className)}>
        <Loader2 className="w-5 h-5 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (error || !summary) {
    return (
      <div className={cn('text-sm text-muted-foreground p-4', className)}>
        Unable to load learning insights
      </div>
    )
  }

  const getProgressColor = (percentage: number) => {
    if (percentage >= 75) return 'text-green-400'
    if (percentage >= 50) return 'text-blue-400'
    if (percentage >= 25) return 'text-yellow-400'
    return 'text-zinc-400'
  }

  const getProgressBg = (percentage: number) => {
    if (percentage >= 75) return 'bg-green-500'
    if (percentage >= 50) return 'bg-blue-500'
    if (percentage >= 25) return 'bg-yellow-500'
    return 'bg-zinc-500'
  }

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'improving': return <TrendingUp className="w-3 h-3 text-green-400" />
      case 'declining': return <TrendingUp className="w-3 h-3 text-red-400 rotate-180" />
      default: return <span className="w-3 h-3 text-zinc-400">—</span>
    }
  }

  if (compact) {
    return (
      <div className={cn('space-y-3', className)}>
        {/* Header */}
        <div className="flex items-center gap-2">
          <Brain className="w-4 h-4 text-primary" />
          <span className="text-sm font-medium">Learning</span>
        </div>

        {/* Quick stats */}
        <div className="grid grid-cols-2 gap-2">
          <QuickStat
            icon={<User className="w-3.5 h-3.5" />}
            label="Profile"
            value={`${Math.round(summary.profile.completion_percentage)}%`}
            color={getProgressColor(summary.profile.completion_percentage)}
          />
          <QuickStat
            icon={<Star className="w-3.5 h-3.5" />}
            label="Skills"
            value={summary.skills.total_skills.toString()}
            color="text-purple-400"
          />
          <QuickStat
            icon={<Target className="w-3.5 h-3.5" />}
            label="Goals"
            value={`${summary.goals.completed_goals}/${summary.goals.total_goals}`}
            color="text-blue-400"
          />
          <QuickStat
            icon={<Sparkles className="w-3.5 h-3.5" />}
            label="Agents"
            value={summary.agents.total_agents_used.toString()}
            color="text-amber-400"
          />
        </div>

        {/* Priority action */}
        {summary.profile.priority_field && (
          <div className="bg-primary/10 rounded-lg p-2">
            <div className="flex items-center gap-2 text-xs">
              <Lightbulb className="w-3.5 h-3.5 text-primary" />
              <span className="text-muted-foreground">Complete your</span>
              <span className="text-primary font-medium">{summary.profile.priority_field}</span>
            </div>
          </div>
        )}
      </div>
    )
  }

  // Full panel view
  return (
    <div className={cn('space-y-4', className)}>
      {/* Header */}
      <div className="flex items-center gap-2">
        <Brain className="w-5 h-5 text-primary" />
        <h3 className="text-lg font-semibold">Learning Insights</h3>
      </div>

      {/* Profile Section */}
      <div className="bg-muted/30 rounded-lg p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <User className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm font-medium">Profile Completeness</span>
          </div>
          <span className={cn('text-sm font-medium', getProgressColor(summary.profile.completion_percentage))}>
            {Math.round(summary.profile.completion_percentage)}%
          </span>
        </div>
        <div className="h-2 bg-muted rounded-full overflow-hidden mb-2">
          <div
            className={cn('h-full transition-all', getProgressBg(summary.profile.completion_percentage))}
            style={{ width: `${summary.profile.completion_percentage}%` }}
          />
        </div>
        {summary.profile.missing_fields.length > 0 && (
          <div className="text-xs text-muted-foreground">
            Missing: {summary.profile.missing_fields.slice(0, 3).join(', ')}
            {summary.profile.missing_fields.length > 3 && ` +${summary.profile.missing_fields.length - 3} more`}
          </div>
        )}
      </div>

      {/* Agent Effectiveness */}
      <div className="bg-muted/30 rounded-lg p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm font-medium">Agent Effectiveness</span>
          </div>
          <div className="flex items-center gap-1">
            {getTrendIcon(summary.agents.recent_trend)}
            <span className="text-xs text-muted-foreground capitalize">{summary.agents.recent_trend}</span>
          </div>
        </div>

        {summary.agents.top_agents.length > 0 ? (
          <div className="space-y-2">
            {summary.agents.top_agents.slice(0, 3).map((agent) => (
              <div key={agent.agent_id} className="flex items-center justify-between">
                <span className="text-sm truncate">{agent.agent_name}</span>
                <div className="flex items-center gap-2">
                  <div className="w-16 h-1.5 bg-muted rounded-full overflow-hidden">
                    <div
                      className={cn('h-full', getProgressBg(agent.effectiveness_score * 100))}
                      style={{ width: `${agent.effectiveness_score * 100}%` }}
                    />
                  </div>
                  <span className="text-xs text-muted-foreground w-8 text-right">
                    {Math.round(agent.effectiveness_score * 100)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-sm text-muted-foreground">
            No feedback recorded yet. Rate responses to improve personalization!
          </div>
        )}
      </div>

      {/* Skills Overview */}
      <div className="bg-muted/30 rounded-lg p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <BarChart3 className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm font-medium">Skills</span>
          </div>
          <span className="text-xs text-muted-foreground">
            {summary.skills.total_skills} tracked
          </span>
        </div>

        {summary.skills.top_skills.length > 0 ? (
          <div className="space-y-2">
            {summary.skills.top_skills.slice(0, 4).map((skill, i) => (
              <div key={i} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-sm">{skill.name}</span>
                  {skill.recent_growth > 0 && (
                    <TrendingUp className="w-3 h-3 text-green-400" />
                  )}
                </div>
                <div className="flex items-center gap-1">
                  {Array.from({ length: 5 }).map((_, j) => (
                    <div
                      key={j}
                      className={cn(
                        'w-1.5 h-3 rounded-sm',
                        j < Math.ceil(skill.level / 20) ? 'bg-primary' : 'bg-muted'
                      )}
                    />
                  ))}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-sm text-muted-foreground">
            Skills will be tracked based on your work
          </div>
        )}

        {summary.skills.learning_velocity > 0 && (
          <div className="mt-3 pt-3 border-t border-muted/50">
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <TrendingUp className="w-3 h-3 text-green-400" />
              <span>Learning velocity: {summary.skills.learning_velocity.toFixed(1)} skills/week</span>
            </div>
          </div>
        )}
      </div>

      {/* Goals Summary */}
      <div className="bg-muted/30 rounded-lg p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Target className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm font-medium">Goals Progress</span>
          </div>
          <button className="text-xs text-primary hover:underline flex items-center gap-1">
            View all <ChevronRight className="w-3 h-3" />
          </button>
        </div>

        <div className="grid grid-cols-3 gap-3 text-center">
          <div>
            <div className="text-2xl font-bold text-blue-400">{summary.goals.active_goals}</div>
            <div className="text-xs text-muted-foreground">Active</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-green-400">{summary.goals.completed_goals}</div>
            <div className="text-xs text-muted-foreground">Completed</div>
          </div>
          <div>
            <div className={cn('text-2xl font-bold', getProgressColor(summary.goals.overall_progress))}>
              {Math.round(summary.goals.overall_progress)}%
            </div>
            <div className="text-xs text-muted-foreground">Progress</div>
          </div>
        </div>
      </div>
    </div>
  )
}

function QuickStat({
  icon,
  label,
  value,
  color,
}: {
  icon: React.ReactNode
  label: string
  value: string
  color: string
}) {
  return (
    <div className="bg-muted/30 rounded-lg p-2">
      <div className="flex items-center gap-1.5 mb-0.5">
        <span className="text-muted-foreground">{icon}</span>
        <span className="text-xs text-muted-foreground">{label}</span>
      </div>
      <div className={cn('text-sm font-medium', color)}>{value}</div>
    </div>
  )
}

export default LearningInsightsPanel
