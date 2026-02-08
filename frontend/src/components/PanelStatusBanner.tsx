// Session 968: Unified status banner for workspace panels
import { AlertCircle, Unplug, RefreshCw, InboxIcon } from 'lucide-react'
import { cn } from '@/lib/cn'

type PanelStatus = 'ok' | 'empty' | 'error' | 'unwired'

interface PanelStatusBannerProps {
  status: PanelStatus
  message?: string
  endpoint?: string
  onRetry?: () => void
  error?: Error | null
  className?: string
}

export function PanelStatusBanner({
  status,
  message,
  endpoint,
  onRetry,
  error,
  className,
}: PanelStatusBannerProps) {
  if (status === 'ok') return null

  if (status === 'empty') {
    return (
      <div className={cn('flex flex-col items-center justify-center py-10 text-center', className)}>
        <div className="h-10 w-10 rounded-full bg-yellow-500/10 flex items-center justify-center mb-3">
          <InboxIcon className="text-yellow-400" size={20} />
        </div>
        <p className="text-sm font-medium text-gray-300 mb-1">No data available</p>
        {message && <p className="text-xs text-gray-500 max-w-sm">{message}</p>}
        {onRetry && (
          <button
            onClick={onRetry}
            className="mt-3 flex items-center gap-1.5 px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-white rounded text-xs transition-colors"
          >
            <RefreshCw size={12} />
            Refresh
          </button>
        )}
      </div>
    )
  }

  if (status === 'error') {
    const errorMsg = message || error?.message || 'An error occurred while loading data'
    return (
      <div className={cn('flex flex-col items-center justify-center py-10 text-center', className)}>
        <div className="h-10 w-10 rounded-full bg-red-500/20 flex items-center justify-center mb-3">
          <AlertCircle className="text-red-400" size={20} />
        </div>
        <p className="text-sm font-medium text-white mb-1">Failed to Load</p>
        <p className="text-xs text-gray-400 max-w-sm mb-3">{errorMsg}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-white rounded text-xs transition-colors"
          >
            <RefreshCw size={12} />
            Try Again
          </button>
        )}
      </div>
    )
  }

  // unwired
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center py-10 text-center border border-dashed border-gray-700 rounded-lg bg-gray-900/30',
        className
      )}
    >
      <div className="h-10 w-10 rounded-full bg-gray-700/40 flex items-center justify-center mb-3">
        <Unplug className="text-gray-500" size={20} />
      </div>
      <p className="text-sm font-medium text-gray-400 mb-1">Not connected</p>
      <p className="text-xs text-gray-600 max-w-sm">
        {message || 'This panel is not connected to a data source'}
      </p>
      {endpoint && (
        <code className="mt-2 text-[10px] text-gray-600 bg-gray-800/50 px-2 py-0.5 rounded font-mono">
          {endpoint}
        </code>
      )}
    </div>
  )
}
