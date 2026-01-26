// Session 833: Shared error state component for workspace tabs
import { AlertCircle, RefreshCw } from 'lucide-react'
import { cn } from '@/lib/cn'

interface ErrorStateProps {
  error: Error | null
  onRetry?: () => void
  message?: string
  className?: string
}

export function ErrorState({ error, onRetry, message, className }: ErrorStateProps) {
  const errorMessage = message || error?.message || 'An error occurred while loading data'

  return (
    <div className={cn('flex flex-col items-center justify-center py-12 text-center', className)}>
      <div className="h-12 w-12 rounded-full bg-red-500/20 flex items-center justify-center mb-4">
        <AlertCircle className="text-red-400" size={24} />
      </div>
      <h4 className="text-lg font-medium text-white mb-2">Failed to Load</h4>
      <p className="text-sm text-gray-400 max-w-md mb-4">{errorMessage}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg text-sm transition-colors"
        >
          <RefreshCw size={14} />
          Try Again
        </button>
      )}
    </div>
  )
}
