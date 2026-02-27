import { useNavigate } from 'react-router-dom'
import { Bell } from 'lucide-react'
import { useAlerts } from '@/hooks/cockpitQueries'

interface CockpitTopBarProps {
  title: string
  focusMode: boolean
  onCommandPalette: () => void
}

export default function CockpitTopBar({ title, focusMode, onCommandPalette }: CockpitTopBarProps) {
  const navigate = useNavigate()
  const { data: alerts } = useAlerts()
  const alertCount = alerts?.total ?? 0
  const hasHigh = (alerts?.items.filter(a => a.severity === 'critical' || a.severity === 'high').length ?? 0) > 0

  return (
    <header className="flex h-12 items-center justify-between border-b border-dark-border bg-dark-card px-4">
      <div className="flex items-center gap-3">
        <h2 className="text-sm font-semibold text-gray-200">{title}</h2>
        {focusMode && (
          <span className="rounded-full bg-primary-600/20 px-2 py-0.5 text-[11px] font-medium text-primary-400">
            Focus
          </span>
        )}
      </div>
      <div className="flex items-center gap-3">
        <button
          onClick={() => navigate('/cockpit/alerts')}
          className="relative p-1.5 rounded-lg text-gray-400 hover:text-gray-200 hover:bg-dark-border/30 transition-colors"
          title={`${alertCount} alert${alertCount !== 1 ? 's' : ''}`}
        >
          <Bell size={16} />
          {alertCount > 0 && (
            <span className={`absolute -top-0.5 -right-0.5 min-w-[16px] h-4 flex items-center justify-center rounded-full text-[10px] font-bold px-1 ${
              hasHigh ? 'bg-red-500 text-white' : 'bg-primary-600 text-white'
            }`}>
              {alertCount > 99 ? '99+' : alertCount}
            </span>
          )}
        </button>
        <button
          onClick={onCommandPalette}
          className="flex items-center gap-2 rounded-lg border border-dark-border px-3 py-1.5 text-xs text-gray-400 hover:border-gray-600 hover:text-gray-200 transition-colors"
        >
          <span>Search</span>
          <kbd className="rounded bg-dark-bg px-1.5 py-0.5 text-[10px] font-mono text-gray-500">
            {navigator.platform?.includes('Mac') ? '\u2318' : 'Ctrl'}K
          </kbd>
        </button>
      </div>
    </header>
  )
}
