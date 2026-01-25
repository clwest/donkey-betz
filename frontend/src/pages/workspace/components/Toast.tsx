// Session 825: Toast notification component
// Extracted from WorkspacePage.tsx for reuse
import { CheckCircle, XCircle } from 'lucide-react'
import { cn } from '@/lib/cn'
import type { ActionResult } from '../types'

interface ToastProps {
  result: ActionResult
  onClose: () => void
}

export function Toast({ result, onClose }: ToastProps) {
  return (
    <div
      className={cn(
        'fixed bottom-4 right-4 flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg animate-in slide-in-from-bottom-4 z-50',
        result.type === 'success'
          ? 'bg-accent-green/20 text-accent-green border border-accent-green/30'
          : 'bg-accent-red/20 text-accent-red border border-accent-red/30'
      )}
    >
      {result.type === 'success' ? <CheckCircle size={18} /> : <XCircle size={18} />}
      <span className="text-sm">{result.message}</span>
      <button onClick={onClose} className="ml-2 opacity-70 hover:opacity-100">
        &times;
      </button>
    </div>
  )
}
