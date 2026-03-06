import { Target } from 'lucide-react'
import SkeletonRows from '@/components/cockpit/shared/SkeletonRows'
import { useRunsMetrics } from '@/hooks/cockpitQueries'
import type { NorthStarPath } from '@/types/cockpit'

const PATH_COLORS: Record<NorthStarPath, string> = {
  revenue: '#22c55e',
  content: '#3b82f6',
  sports: '#f59e0b',
  none: '#6b7280',
}

const PATH_LABELS: Record<NorthStarPath, string> = {
  revenue: 'Revenue',
  content: 'Content',
  sports: 'Sports',
  none: 'Noise',
}

function DonutChart({ data }: { data: Record<NorthStarPath, { count: number; pct: number }> }) {
  const paths: NorthStarPath[] = ['revenue', 'content', 'sports', 'none']
  const total = paths.reduce((s, p) => s + (data[p]?.pct || 0), 0)
  if (total === 0) return null

  const size = 120
  const strokeWidth = 18
  const radius = (size - strokeWidth) / 2
  const circumference = 2 * Math.PI * radius

  let offset = 0
  const segments = paths.map((path) => {
    const pct = data[path]?.pct || 0
    const dashLength = (pct / 100) * circumference
    const dashOffset = -offset
    offset += dashLength
    return { path, pct, dashLength, dashOffset, color: PATH_COLORS[path] }
  })

  return (
    <div className="flex items-center gap-6">
      <svg width={size} height={size} className="shrink-0 -rotate-90">
        {/* Background ring */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#1f2937"
          strokeWidth={strokeWidth}
        />
        {segments.map((seg) =>
          seg.pct > 0 ? (
            <circle
              key={seg.path}
              cx={size / 2}
              cy={size / 2}
              r={radius}
              fill="none"
              stroke={seg.color}
              strokeWidth={strokeWidth}
              strokeDasharray={`${seg.dashLength} ${circumference - seg.dashLength}`}
              strokeDashoffset={seg.dashOffset}
              className="transition-all duration-500"
            />
          ) : null,
        )}
      </svg>

      <div className="space-y-1.5">
        {segments.map((seg) => (
          <div key={seg.path} className="flex items-center gap-2 text-sm">
            <span
              className="inline-block h-2.5 w-2.5 rounded-full"
              style={{ backgroundColor: seg.color }}
            />
            <span className="text-gray-300">{PATH_LABELS[seg.path]}</span>
            <span className="text-gray-500 tabular-nums">{seg.pct}%</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default function NorthStarCard() {
  const { data, isLoading } = useRunsMetrics(24)

  const ns = data?.north_star_coverage
  const onTrack = ns ? (ns.revenue?.pct || 0) + (ns.content?.pct || 0) + (ns.sports?.pct || 0) : 0

  return (
    <div className="card flex flex-col">
      <div className="flex items-center justify-between border-b border-dark-border px-4 py-3">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-200">
          <Target size={16} className="text-primary-400" />
          North Star Coverage
          {ns && (
            <span className={`rounded-full px-2 py-0.5 text-[11px] font-medium ${
              onTrack >= 70 ? 'bg-green-500/20 text-green-400' :
              onTrack >= 40 ? 'bg-amber-500/20 text-amber-400' :
              'bg-red-500/20 text-red-400'
            }`}>
              {Math.round(onTrack)}% on-track
            </span>
          )}
        </div>
        <span className="text-xs text-gray-500">24h</span>
      </div>

      <div className="flex-1 p-4">
        {isLoading ? (
          <SkeletonRows count={4} />
        ) : !ns ? (
          <p className="text-sm text-gray-500 text-center py-6">No data</p>
        ) : (
          <div className="space-y-4">
            <DonutChart data={ns} />
            <div className="text-xs text-gray-500">
              {data?.total_runs ?? 0} runs sampled
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
