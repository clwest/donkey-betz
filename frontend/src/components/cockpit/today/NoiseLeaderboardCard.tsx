import { BarChart3 } from 'lucide-react'
import SkeletonRows from '@/components/cockpit/shared/SkeletonRows'
import { useConversationMetrics } from '@/hooks/cockpitQueries'

export default function NoiseLeaderboardCard() {
  const { data, isLoading } = useConversationMetrics(24)

  const topics = data?.top_topics ?? []
  const zombieRate = data?.zombie_rate
  const maxCount = topics.length > 0 ? topics[0].count : 1

  return (
    <div className="card flex flex-col">
      <div className="flex items-center justify-between border-b border-dark-border px-4 py-3">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-200">
          <BarChart3 size={16} className="text-amber-400" />
          Conversation Topics
          {data && (
            <span className="rounded-full bg-dark-border px-2 py-0.5 text-[11px] font-medium text-gray-400">
              {data.total_conversations}
            </span>
          )}
        </div>
        <span className="text-xs text-gray-500">24h</span>
      </div>

      <div className="flex-1 p-4">
        {isLoading ? (
          <SkeletonRows count={6} />
        ) : topics.length === 0 ? (
          <p className="text-sm text-gray-500 text-center py-6">No conversations</p>
        ) : (
          <div className="space-y-3">
            <ul className="space-y-2">
              {topics.slice(0, 8).map((t) => (
                <li key={t.topic} className="flex items-center gap-3">
                  <span className="text-sm text-gray-300 w-36 truncate" title={t.topic}>
                    {t.topic}
                  </span>
                  <div className="flex-1 h-2 rounded-full bg-dark-border overflow-hidden">
                    <div
                      className="h-full rounded-full bg-primary-500/60 transition-all duration-300"
                      style={{ width: `${(t.count / maxCount) * 100}%` }}
                    />
                  </div>
                  <span className="text-xs text-gray-500 tabular-nums w-6 text-right">
                    {t.count}
                  </span>
                </li>
              ))}
            </ul>

            {zombieRate && zombieRate.total > 0 && (
              <div className="flex items-center gap-2 pt-2 border-t border-dark-border">
                <span className="text-xs text-gray-500">Zombie conversations:</span>
                <span className={`text-xs font-medium tabular-nums ${
                  zombieRate.pct > 30 ? 'text-red-400' :
                  zombieRate.pct > 15 ? 'text-amber-400' :
                  'text-gray-400'
                }`}>
                  {zombieRate.zombies}/{zombieRate.total} ({zombieRate.pct}%)
                </span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
