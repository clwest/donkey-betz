import { Shield, ShieldAlert } from 'lucide-react'
import SkeletonRows from '@/components/cockpit/shared/SkeletonRows'
import { useFocusModeStatus, useUpdateFocusMode } from '@/hooks/cockpitQueries'

export default function FocusModeCard() {
  const { data, isLoading } = useFocusModeStatus()
  const update = useUpdateFocusMode()

  const toggleEnabled = () => {
    if (!data) return
    update.mutate({ enabled: !data.enabled })
  }

  const toggleMode = () => {
    if (!data) return
    update.mutate({ mode: data.mode === 'gentle' ? 'strict' : 'gentle' })
  }

  return (
    <div className="card flex flex-col">
      <div className="flex items-center justify-between border-b border-dark-border px-4 py-3">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-200">
          {data?.enabled ? (
            <Shield size={16} className="text-green-400" />
          ) : (
            <ShieldAlert size={16} className="text-gray-500" />
          )}
          Focus Mode
          {data && (
            <span className={`rounded-full px-2 py-0.5 text-[11px] font-medium ${
              data.enabled
                ? 'bg-green-500/20 text-green-400'
                : 'bg-gray-500/20 text-gray-400'
            }`}>
              {data.enabled ? data.mode : 'off'}
            </span>
          )}
        </div>
      </div>

      <div className="flex-1 p-4">
        {isLoading ? (
          <SkeletonRows count={4} />
        ) : !data ? (
          <p className="text-sm text-gray-500 text-center py-6">Unavailable</p>
        ) : (
          <div className="space-y-3">
            {/* Toggle row */}
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-300">Enabled</span>
              <button
                onClick={toggleEnabled}
                disabled={update.isPending}
                className={`relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full transition-colors duration-200 ${
                  data.enabled ? 'bg-green-500' : 'bg-gray-600'
                }`}
              >
                <span className={`inline-block h-4 w-4 rounded-full bg-white shadow transform transition-transform duration-200 mt-0.5 ${
                  data.enabled ? 'translate-x-4 ml-0.5' : 'translate-x-0.5'
                }`} />
              </button>
            </div>

            {/* Mode toggle */}
            {data.enabled && (
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-300">Mode</span>
                <button
                  onClick={toggleMode}
                  disabled={update.isPending}
                  className="text-xs px-2 py-1 rounded bg-dark-border text-gray-300 hover:text-white transition-colors"
                >
                  {data.mode === 'gentle' ? 'Gentle' : 'Strict'}
                </button>
              </div>
            )}

            {/* Stats */}
            <div className="space-y-1.5 pt-2 border-t border-dark-border">
              <div className="flex justify-between text-xs">
                <span className="text-gray-500">Blocks (24h)</span>
                <span className="text-gray-300 tabular-nums">{data.blocks_24h}</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-gray-500">Agent cap</span>
                <span className="text-gray-300 tabular-nums">{data.max_conversations_per_agent_per_hour}/hr</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-gray-500">Total cap</span>
                <span className="text-gray-300 tabular-nums">{data.max_total_conversations_per_hour}/hr</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-gray-500">Blocked topics</span>
                <span className="text-gray-300 tabular-nums">{data.blocked_topics.length}</span>
              </div>
              {data.require_north_star && (
                <div className="flex justify-between text-xs">
                  <span className="text-gray-500">North Star required</span>
                  <span className="text-green-400">Yes</span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
