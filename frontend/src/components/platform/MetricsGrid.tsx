/**
 * Session 815: Metrics Grid Component
 *
 * Displays 4-card grid for mission metrics with progress bars.
 * Part of the Platform Command Center.
 */

import { DollarSign, Cpu, BookOpen, FileText } from 'lucide-react'
import { cn } from '@/lib/cn'

interface MetricItem {
  current: number
  target: number
  progress_pct: number
}

interface MetricsSummary {
  revenue: MetricItem
  llm_cost: MetricItem
  canon: MetricItem
  playbooks: MetricItem
}

interface MetricsGridProps {
  metrics?: MetricsSummary
  isLoading?: boolean
}

interface MetricCardProps {
  label: string
  icon: React.ElementType
  current: number
  target: number
  progressPct: number
  color: string
  format?: 'currency' | 'number'
  invertProgress?: boolean // For costs, lower is better
}

function MetricCard({
  label,
  icon: Icon,
  current,
  target,
  progressPct,
  color,
  format = 'number',
  invertProgress = false,
}: MetricCardProps) {
  const displayValue = format === 'currency'
    ? `$${current.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`
    : current.toLocaleString()

  const displayTarget = format === 'currency'
    ? `$${target.toLocaleString()}`
    : target.toLocaleString()

  // For inverted metrics (like cost), good = low percentage
  const isGood = invertProgress ? progressPct < 80 : progressPct >= 50
  const isCritical = invertProgress ? progressPct >= 100 : progressPct < 20

  const progressColor = isCritical
    ? 'bg-accent-red'
    : isGood
      ? 'bg-accent-green'
      : 'bg-accent-amber'

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm text-gray-400">{label}</span>
        <div
          className="h-8 w-8 rounded-lg flex items-center justify-center"
          style={{ backgroundColor: `${color}20` }}
        >
          <Icon size={16} style={{ color }} />
        </div>
      </div>

      <div className="mb-2">
        <span className="text-2xl font-bold text-white">{displayValue}</span>
        <span className="text-sm text-gray-500 ml-2">
          {invertProgress ? 'max' : 'of'} {displayTarget}
        </span>
      </div>

      {/* Progress Bar */}
      <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
        <div
          className={cn('h-full rounded-full transition-all duration-500', progressColor)}
          style={{ width: `${Math.min(100, progressPct)}%` }}
        />
      </div>

      <div className="flex justify-between mt-1 text-xs text-gray-500">
        <span>{progressPct.toFixed(0)}%</span>
        <span>{invertProgress ? 'of budget' : 'complete'}</span>
      </div>
    </div>
  )
}

export function MetricsGrid({ metrics, isLoading }: MetricsGridProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="card animate-pulse">
            <div className="h-4 bg-gray-700 rounded w-1/2 mb-3"></div>
            <div className="h-8 bg-gray-700 rounded w-2/3 mb-2"></div>
            <div className="h-2 bg-gray-700 rounded w-full"></div>
          </div>
        ))}
      </div>
    )
  }

  if (!metrics) {
    return null
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <MetricCard
        label="Monthly Revenue"
        icon={DollarSign}
        current={metrics.revenue.current}
        target={metrics.revenue.target}
        progressPct={metrics.revenue.progress_pct}
        color="#22c55e"
        format="currency"
      />
      <MetricCard
        label="Daily LLM Cost"
        icon={Cpu}
        current={metrics.llm_cost.current}
        target={metrics.llm_cost.target}
        progressPct={metrics.llm_cost.progress_pct}
        color="#f59e0b"
        format="currency"
        invertProgress
      />
      <MetricCard
        label="Canon Docs"
        icon={BookOpen}
        current={metrics.canon.current}
        target={metrics.canon.target}
        progressPct={metrics.canon.progress_pct}
        color="#8b5cf6"
      />
      <MetricCard
        label="Playbooks"
        icon={FileText}
        current={metrics.playbooks.current}
        target={metrics.playbooks.target}
        progressPct={metrics.playbooks.progress_pct}
        color="#06b6d4"
      />
    </div>
  )
}
