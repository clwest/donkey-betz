/**
 * Session 815: Mission Card Component
 *
 * Displays the current platform mission with status and goal.
 * Part of the Platform Command Center.
 */

import { Target, User, Calendar, TrendingUp } from 'lucide-react'
import { cn } from '@/lib/cn'

interface MissionData {
  status: string
  statement: string
  goal: string
  period: string
  session?: number
  priorities?: Array<{
    rank: number
    name: string
    why: string
  }>
}

interface MissionCardProps {
  mission?: MissionData
  isLoading?: boolean
}

export function MissionCard({ mission, isLoading }: MissionCardProps) {
  if (isLoading) {
    return (
      <div className="card animate-pulse">
        <div className="h-6 bg-gray-700 rounded w-1/3 mb-4"></div>
        <div className="h-4 bg-gray-700 rounded w-full mb-2"></div>
        <div className="h-4 bg-gray-700 rounded w-2/3"></div>
      </div>
    )
  }

  if (!mission) {
    return (
      <div className="card border border-gray-700">
        <div className="flex items-center gap-3 text-gray-400">
          <Target size={24} />
          <span>No mission defined</span>
        </div>
      </div>
    )
  }

  const statusColor = mission.status === 'active'
    ? 'text-accent-green'
    : mission.status === 'paused'
      ? 'text-accent-amber'
      : 'text-gray-400'

  return (
    <div className="card border border-accent-purple/30 bg-gradient-to-br from-accent-purple/10 to-transparent">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-lg bg-accent-purple/20 flex items-center justify-center">
            <Target className="text-accent-purple" size={20} />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">MISSION</h3>
            <span className={cn('text-xs uppercase font-medium', statusColor)}>
              {mission.status}
            </span>
          </div>
        </div>

        {mission.session && (
          <span className="text-xs text-gray-500 font-mono">
            Session {mission.session}
          </span>
        )}
      </div>

      {/* Mission Statement */}
      <blockquote className="text-lg text-white font-medium mb-4 pl-4 border-l-2 border-accent-purple">
        {mission.statement}
      </blockquote>

      {/* Goal */}
      <div className="flex items-center gap-2 text-sm text-gray-300 mb-4">
        <TrendingUp size={14} className="text-accent-green" />
        <span className="font-medium">Goal:</span>
        <span>{mission.goal}</span>
      </div>

      {/* Meta Info */}
      <div className="flex items-center gap-6 text-xs text-gray-500 border-t border-gray-700/50 pt-3 mt-3">
        <div className="flex items-center gap-2">
          <Calendar size={12} />
          <span>{mission.period}</span>
        </div>
        <div className="flex items-center gap-2">
          <User size={12} />
          <span>Chris West</span>
        </div>
      </div>

      {/* Priorities Preview */}
      {mission.priorities && mission.priorities.length > 0 && (
        <div className="mt-4 pt-3 border-t border-gray-700/50">
          <h4 className="text-xs uppercase text-gray-500 font-medium mb-2">Top Priorities</h4>
          <div className="flex flex-wrap gap-2">
            {mission.priorities.slice(0, 3).map((p) => (
              <span
                key={p.rank}
                className="text-xs px-2 py-1 rounded bg-gray-700/50 text-gray-300"
              >
                {p.rank}. {p.name}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
