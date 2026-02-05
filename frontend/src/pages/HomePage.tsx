/**
 * Session 884: AI OS Boot Experience - Home Page
 * Session 935: Added learning widgets
 *
 * The "boot experience" that makes users feel like they're starting up
 * their AI operating system. Shows personalized greeting, activity since
 * last visit, active projects, and natural language input.
 */

import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { homeApi } from '@/lib/api'
import {
  Send,
  Loader2,
  Bug,
  Lightbulb,
  TrendingUp,
  CheckCircle,
  AlertCircle,
  Search,
  Hammer,
  FileText,
  Microscope,
  Scale,
  Wrench,
} from 'lucide-react'
import { cn } from '@/lib/cn'
// Session 935: User Learning Components
import { GoalProgressDashboard } from '@/components/GoalProgressDashboard'
import { LearningInsightsPanel } from '@/components/LearningInsightsPanel'

// Types for API response
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
  }
  active_projects: Array<{
    id: string
    name: string
    type: string
    completion_percentage: number
    status: string
    current_stage: number
    pending_decision: {
      stage: number
      title: string
    } | null
  }>
  quick_stats: {
    agents_active: number
    system_health: 'healthy' | 'degraded'
  }
}

// Greeting component
function BootGreeting({ greeting }: { greeting?: BootData['greeting'] }) {
  if (!greeting) return null

  const timeGreeting = {
    morning: 'Good morning',
    afternoon: 'Good afternoon',
    evening: 'Good evening',
  }[greeting.time_of_day]

  return (
    <div className="text-center space-y-2">
      <h1 className="text-3xl font-bold text-white">
        {timeGreeting}, {greeting.user_name}.
      </h1>
      <p className="text-lg text-gray-400">
        Your AI partner is ready. What shall we accomplish together?
      </p>
    </div>
  )
}

// While Away section - shows activity since last visit
function WhileAwaySection({ whileAway }: { whileAway?: BootData['while_away'] }) {
  const navigate = useNavigate()

  if (!whileAway) return null

  // Don't show if user was away less than an hour and nothing happened
  const hasActivity =
    whileAway.spider_findings > 0 ||
    whileAway.high_score_dreams > 0 ||
    whileAway.initiatives_progressed > 0

  if (whileAway.hours_since_visit < 1 && !hasActivity) return null

  const items = [
    {
      icon: Bug,
      count: whileAway.spider_findings,
      label: 'findings',
      color: 'text-blue-400',
      bgColor: 'bg-blue-400/10',
      onClick: () => navigate('/workspace?tab=datasources'),
    },
    {
      icon: Lightbulb,
      count: whileAway.high_score_dreams,
      label: 'promising ideas',
      color: 'text-yellow-400',
      bgColor: 'bg-yellow-400/10',
      onClick: () => navigate('/workspace?tab=command'),
    },
    {
      icon: TrendingUp,
      count: whileAway.initiatives_progressed,
      label: 'initiatives moved',
      color: 'text-green-400',
      bgColor: 'bg-green-400/10',
      onClick: () => navigate('/workspace?tab=content'),
    },
  ].filter((item) => item.count > 0)

  if (items.length === 0) return null

  return (
    <div className="space-y-3">
      <h2 className="text-sm font-medium text-gray-500 uppercase tracking-wide">
        While you were away
      </h2>
      <div className="flex flex-wrap gap-3 justify-center">
        {items.map((item, idx) => (
          <button
            key={idx}
            onClick={item.onClick}
            className={cn(
              'flex items-center gap-2 px-4 py-2 rounded-lg transition-all',
              item.bgColor,
              'hover:scale-105 hover:shadow-lg'
            )}
          >
            <item.icon size={18} className={item.color} />
            <span className={cn('font-semibold', item.color)}>{item.count}</span>
            <span className="text-gray-400">{item.label}</span>
          </button>
        ))}
      </div>
    </div>
  )
}

// Active Projects section
function ActiveProjectsSection({
  projects,
}: {
  projects?: BootData['active_projects']
}) {
  const navigate = useNavigate()

  if (!projects || projects.length === 0) return null

  return (
    <div className="space-y-3">
      <h2 className="text-sm font-medium text-gray-500 uppercase tracking-wide">
        Active Projects
      </h2>
      <div className="space-y-2">
        {projects.map((project) => (
          <button
            key={project.id}
            onClick={() => navigate(`/workspace?tab=content&initiative=${project.id}`)}
            className="w-full p-4 rounded-lg bg-dark-card border border-dark-border hover:border-primary-500/50 transition-all text-left"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium text-white">{project.name}</span>
              <span
                className={cn(
                  'text-xs px-2 py-1 rounded-full',
                  project.status === 'decision_pending'
                    ? 'bg-yellow-400/10 text-yellow-400'
                    : 'bg-green-400/10 text-green-400'
                )}
              >
                {project.status === 'decision_pending'
                  ? 'Decision pending'
                  : 'On track'}
              </span>
            </div>
            <div className="flex items-center gap-3">
              {/* Progress bar */}
              <div className="flex-1 h-2 bg-dark-border rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary-500 rounded-full transition-all"
                  style={{ width: `${project.completion_percentage}%` }}
                />
              </div>
              <span className="text-sm text-gray-500">
                Stage {project.current_stage}/5
              </span>
            </div>
            {project.pending_decision && (
              <div className="mt-2 flex items-center gap-2 text-yellow-400 text-sm">
                <AlertCircle size={14} />
                <span>{project.pending_decision.title}</span>
              </div>
            )}
          </button>
        ))}
      </div>
    </div>
  )
}

// Natural Language Input
function NaturalLanguageInput({
  onSubmit,
}: {
  onSubmit: (message: string) => void
}) {
  const [input, setInput] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (input.trim()) {
      onSubmit(input.trim())
      setInput('')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="relative">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="What are we working on today?"
        className="w-full px-6 py-4 rounded-xl bg-dark-card border border-dark-border text-white placeholder-gray-500 focus:outline-none focus:border-primary-500 focus:ring-1 focus:ring-primary-500 pr-14 text-lg"
      />
      <button
        type="submit"
        disabled={!input.trim()}
        className={cn(
          'absolute right-3 top-1/2 -translate-y-1/2 p-2 rounded-lg transition-all',
          input.trim()
            ? 'bg-primary-600 text-white hover:bg-primary-500'
            : 'bg-dark-border text-gray-500'
        )}
      >
        <Send size={20} />
      </button>
    </form>
  )
}

// Quick Actions Bar
function QuickActionsBar({
  onAction,
}: {
  onAction: (action: string) => void
}) {
  const actions = [
    {
      label: 'Create',
      icon: FileText,
      action: 'create',
      prompt: 'Help me create ',
    },
    {
      label: 'Research',
      icon: Microscope,
      action: 'research',
      prompt: 'Research ',
    },
    {
      label: 'Decide',
      icon: Scale,
      action: 'decide',
      prompt: 'Help me decide ',
    },
    {
      label: 'Review',
      icon: Search,
      action: 'review',
      prompt: 'Review my ',
    },
    {
      label: 'Build',
      icon: Hammer,
      action: 'build',
      prompt: 'Help me build ',
    },
  ]

  return (
    <div className="flex flex-wrap justify-center gap-3">
      {actions.map((action) => (
        <button
          key={action.action}
          onClick={() => onAction(action.prompt)}
          className="flex items-center gap-2 px-4 py-2 rounded-lg bg-dark-card border border-dark-border hover:border-primary-500/50 hover:bg-dark-card/80 transition-all text-gray-300 hover:text-white"
        >
          <action.icon size={16} />
          <span>{action.label}</span>
        </button>
      ))}
    </div>
  )
}

// System Status indicator (subtle footer)
function SystemStatus({ stats }: { stats?: BootData['quick_stats'] }) {
  if (!stats) return null

  return (
    <div className="flex items-center justify-center gap-4 text-sm text-gray-500">
      <div className="flex items-center gap-2">
        {stats.system_health === 'healthy' ? (
          <CheckCircle size={14} className="text-green-400" />
        ) : (
          <AlertCircle size={14} className="text-yellow-400" />
        )}
        <span>
          {stats.system_health === 'healthy' ? 'All systems ready' : 'Limited capacity'}
        </span>
      </div>
      <span className="text-gray-600">|</span>
      <div className="flex items-center gap-2">
        <Wrench size={14} />
        <span>{stats.agents_active} agents active</span>
      </div>
    </div>
  )
}

// Main HomePage component
export default function HomePage() {
  const navigate = useNavigate()

  // Fetch boot data
  const { data, isLoading, error } = useQuery({
    queryKey: ['home-boot'],
    queryFn: async () => {
      const response = await homeApi.boot()
      return response.data as BootData
    },
    refetchInterval: 60000, // Refresh every minute
  })

  // Handle natural language input - navigate to assistant with prefilled message
  const handleSubmit = (message: string) => {
    // Navigate to assistant page with the message as a query param
    navigate(`/assistant?message=${encodeURIComponent(message)}`)
  }

  // Handle quick action - prefill the input placeholder behavior
  const handleQuickAction = (prompt: string) => {
    // Navigate to assistant with the partial prompt
    navigate(`/assistant?message=${encodeURIComponent(prompt)}`)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center space-y-4">
          <Loader2 size={48} className="animate-spin text-primary-500 mx-auto" />
          <p className="text-gray-400">Booting AI OS...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center space-y-4">
          <AlertCircle size={48} className="text-red-400 mx-auto" />
          <p className="text-gray-400">Failed to load home page</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 rounded-lg bg-primary-600 text-white hover:bg-primary-500"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto space-y-10 py-12 px-4">
      {/* Greeting */}
      <BootGreeting greeting={data?.greeting} />

      {/* While Away */}
      <WhileAwaySection whileAway={data?.while_away} />

      {/* Active Projects */}
      <ActiveProjectsSection projects={data?.active_projects} />

      {/* Session 935: Learning & Goals Section */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <GoalProgressDashboard compact maxItems={3} />
        </div>
        <div className="bg-dark-card border border-dark-border rounded-lg p-4">
          <LearningInsightsPanel compact />
        </div>
      </div>

      {/* Natural Language Input */}
      <div className="space-y-4">
        <NaturalLanguageInput onSubmit={handleSubmit} />
        <QuickActionsBar onAction={handleQuickAction} />
      </div>

      {/* System Status */}
      <SystemStatus stats={data?.quick_stats} />
    </div>
  )
}
