/**
 * Session 935: Goal Progress Dashboard Component
 *
 * Displays user goals with progress bars and status indicators.
 * Allows recording manual progress updates.
 */

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Target,
  ChevronRight,
  ChevronDown,
  Plus,
  Check,
  Clock,
  TrendingUp,
  AlertCircle,
  Loader2,
  Trophy,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { userLearningApi } from '@/lib/api'

interface Goal {
  id: string
  name: string
  category: string
  target_value: number
  current_value: number
  progress_percentage: number
  status: 'active' | 'completed' | 'paused' | 'abandoned'
  target_date?: string
  days_remaining?: number
}

interface GoalsDashboard {
  goals: Goal[]
  total_goals: number
  active_goals: number
  completed_goals: number
  overall_progress: number
}

interface GoalProgressDashboardProps {
  /** Compact mode for sidebar */
  compact?: boolean
  /** Maximum goals to show in compact mode */
  maxItems?: number
  /** Additional classes */
  className?: string
}

const STATUS_CONFIG = {
  active: { icon: TrendingUp, color: 'text-blue-400', bg: 'bg-blue-400/10' },
  completed: { icon: Trophy, color: 'text-green-400', bg: 'bg-green-400/10' },
  paused: { icon: Clock, color: 'text-yellow-400', bg: 'bg-yellow-400/10' },
  abandoned: { icon: AlertCircle, color: 'text-zinc-400', bg: 'bg-zinc-400/10' },
}

const CATEGORY_COLORS: Record<string, string> = {
  income: 'bg-green-500',
  skills: 'bg-blue-500',
  content: 'bg-purple-500',
  learning: 'bg-amber-500',
  health: 'bg-pink-500',
  career: 'bg-cyan-500',
  default: 'bg-zinc-500',
}

export function GoalProgressDashboard({
  compact = false,
  maxItems = 5,
  className,
}: GoalProgressDashboardProps) {
  const [expandedGoalId, setExpandedGoalId] = useState<string | null>(null)
  const [progressInput, setProgressInput] = useState<string>('')
  const queryClient = useQueryClient()

  const { data, isLoading, error } = useQuery({
    queryKey: ['goals-dashboard'],
    queryFn: async () => {
      const response = await userLearningApi.getGoalsDashboard()
      return response.data as { success: boolean; data: GoalsDashboard }
    },
    refetchInterval: 60000, // Refresh every minute
  })

  const progressMutation = useMutation({
    mutationFn: async ({ goalId, delta }: { goalId: string; delta: number }) => {
      return userLearningApi.recordGoalProgress(goalId, { progress_delta: delta })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['goals-dashboard'] })
      setProgressInput('')
      setExpandedGoalId(null)
    },
  })

  const dashboard = data?.data

  if (isLoading) {
    return (
      <div className={cn('flex items-center justify-center p-4', className)}>
        <Loader2 className="w-5 h-5 animate-spin text-muted-foreground" />
      </div>
    )
  }

  if (error || !dashboard) {
    return (
      <div className={cn('text-sm text-muted-foreground p-4', className)}>
        Unable to load goals
      </div>
    )
  }

  const displayGoals = compact
    ? dashboard.goals.filter(g => g.status === 'active').slice(0, maxItems)
    : dashboard.goals

  const getProgressColor = (percentage: number) => {
    if (percentage >= 75) return 'bg-green-500'
    if (percentage >= 50) return 'bg-blue-500'
    if (percentage >= 25) return 'bg-yellow-500'
    return 'bg-zinc-500'
  }

  return (
    <div className={cn('space-y-3', className)}>
      {/* Header with stats */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Target className="w-4 h-4 text-primary" />
          <span className="text-sm font-medium">Goals</span>
        </div>
        {!compact && (
          <div className="flex items-center gap-3 text-xs text-muted-foreground">
            <span>{dashboard.active_goals} active</span>
            <span>{dashboard.completed_goals} completed</span>
          </div>
        )}
      </div>

      {/* Overall progress (non-compact) */}
      {!compact && dashboard.goals.length > 0 && (
        <div className="bg-muted/30 rounded-lg p-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs text-muted-foreground">Overall Progress</span>
            <span className="text-sm font-medium">{Math.round(dashboard.overall_progress)}%</span>
          </div>
          <div className="h-2 bg-muted rounded-full overflow-hidden">
            <div
              className={cn('h-full transition-all', getProgressColor(dashboard.overall_progress))}
              style={{ width: `${dashboard.overall_progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Goals list */}
      {displayGoals.length === 0 ? (
        <div className="text-sm text-muted-foreground text-center py-4">
          No active goals yet
        </div>
      ) : (
        <div className="space-y-2">
          {displayGoals.map((goal) => {
            const isExpanded = expandedGoalId === goal.id
            const statusConfig = STATUS_CONFIG[goal.status]
            const StatusIcon = statusConfig.icon
            const categoryColor = CATEGORY_COLORS[goal.category] || CATEGORY_COLORS.default

            return (
              <div
                key={goal.id}
                className="bg-muted/30 rounded-lg overflow-hidden"
              >
                {/* Goal header */}
                <button
                  onClick={() => setExpandedGoalId(isExpanded ? null : goal.id)}
                  className="w-full flex items-center gap-3 p-3 hover:bg-muted/50 transition-colors"
                >
                  <div className={cn('w-2 h-2 rounded-full', categoryColor)} />

                  <div className="flex-1 text-left min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium truncate">{goal.name}</span>
                      <StatusIcon className={cn('w-3 h-3 flex-shrink-0', statusConfig.color)} />
                    </div>
                    {!compact && (
                      <div className="text-xs text-muted-foreground">
                        {goal.category} • {goal.days_remaining != null && goal.days_remaining > 0
                          ? `${goal.days_remaining} days left`
                          : goal.status === 'completed' ? 'Completed' : 'No deadline'}
                      </div>
                    )}
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium">
                      {Math.round(goal.progress_percentage)}%
                    </span>
                    {isExpanded ? (
                      <ChevronDown className="w-4 h-4 text-muted-foreground" />
                    ) : (
                      <ChevronRight className="w-4 h-4 text-muted-foreground" />
                    )}
                  </div>
                </button>

                {/* Progress bar */}
                <div className="px-3 pb-2">
                  <div className="h-1.5 bg-muted rounded-full overflow-hidden">
                    <div
                      className={cn('h-full transition-all', getProgressColor(goal.progress_percentage))}
                      style={{ width: `${goal.progress_percentage}%` }}
                    />
                  </div>
                </div>

                {/* Expanded details */}
                {isExpanded && (
                  <div className="px-3 pb-3 pt-1 border-t border-muted/50">
                    <div className="flex items-center justify-between text-xs text-muted-foreground mb-3">
                      <span>{goal.current_value} / {goal.target_value}</span>
                      {goal.target_date && (
                        <span>Target: {new Date(goal.target_date).toLocaleDateString()}</span>
                      )}
                    </div>

                    {/* Quick progress update */}
                    {goal.status === 'active' && (
                      <div className="flex items-center gap-2">
                        <input
                          type="number"
                          placeholder="Add progress"
                          value={progressInput}
                          onChange={(e) => setProgressInput(e.target.value)}
                          className="flex-1 px-2 py-1 text-sm bg-background border border-muted rounded focus:outline-none focus:ring-1 focus:ring-primary"
                        />
                        <button
                          onClick={() => {
                            const delta = parseFloat(progressInput)
                            if (!isNaN(delta) && delta > 0) {
                              progressMutation.mutate({ goalId: goal.id, delta })
                            }
                          }}
                          disabled={progressMutation.isPending || !progressInput}
                          className="p-1.5 bg-primary text-primary-foreground rounded hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          {progressMutation.isPending ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          ) : (
                            <Plus className="w-4 h-4" />
                          )}
                        </button>
                      </div>
                    )}

                    {goal.status === 'completed' && (
                      <div className="flex items-center gap-2 text-green-400">
                        <Check className="w-4 h-4" />
                        <span className="text-sm">Goal achieved!</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}

      {/* Show more link in compact mode */}
      {compact && dashboard.goals.length > maxItems && (
        <button className="text-xs text-primary hover:underline">
          View all {dashboard.total_goals} goals
        </button>
      )}
    </div>
  )
}

export default GoalProgressDashboard
