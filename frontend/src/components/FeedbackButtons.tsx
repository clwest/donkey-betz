/**
 * Session 935: Feedback Buttons Component
 *
 * Thumbs up/down feedback for PA responses and agent outputs.
 * Records feedback to the user learning system for personalization.
 */

import { useState, useCallback } from 'react'
import { ThumbsUp, ThumbsDown, Loader2, Check } from 'lucide-react'
import { cn } from '@/lib/cn'
import { userLearningApi, FeedbackRequest } from '@/lib/api'

interface FeedbackButtonsProps {
  /** Agent ID that generated the response (optional if agentName provided) */
  agentId?: string
  /** Agent name for lookup (optional if agentId provided) */
  agentName?: string
  /** Trace ID from the PA response */
  traceId?: string
  /** Execution ID if available */
  executionId?: string
  /** Deliverable ID if from a deliverable */
  deliverableId?: string
  /** What the user was trying to do */
  taskDescription?: string
  /** Additional context snapshot */
  contextSnapshot?: Record<string, unknown>
  /** Current feedback state (if already provided) */
  initialFeedback?: 'positive' | 'negative' | null
  /** Callback when feedback is recorded */
  onFeedback?: (rating: 1 | -1) => void
  /** Size variant */
  size?: 'sm' | 'md'
  /** Additional classes */
  className?: string
}

type FeedbackState = 'idle' | 'submitting' | 'submitted'

export function FeedbackButtons({
  agentId,
  agentName,
  traceId,
  executionId,
  deliverableId,
  taskDescription,
  contextSnapshot,
  initialFeedback,
  onFeedback,
  size = 'sm',
  className,
}: FeedbackButtonsProps) {
  const [feedback, setFeedback] = useState<'positive' | 'negative' | null>(initialFeedback ?? null)
  const [state, setState] = useState<FeedbackState>('idle')
  const [error, setError] = useState<string | null>(null)

  // Need either agentId or agentName to record feedback
  const canRecordFeedback = !!(agentId || agentName)

  const handleFeedback = useCallback(async (rating: 1 | -1) => {
    // Don't allow changing feedback once submitted
    if (feedback !== null || !canRecordFeedback) return

    setState('submitting')
    setError(null)

    try {
      const request: FeedbackRequest = {
        agent_id: agentId,
        agent_name: agentName,
        rating,
        execution_id: executionId || traceId,  // Use traceId as fallback execution ID
        deliverable_id: deliverableId,
        task_description: taskDescription,
        context_snapshot: contextSnapshot,
      }

      await userLearningApi.recordFeedback(request)

      setFeedback(rating === 1 ? 'positive' : 'negative')
      setState('submitted')
      onFeedback?.(rating)
    } catch (err) {
      console.error('Failed to record feedback:', err)
      setError('Failed to save feedback')
      setState('idle')
    }
  }, [agentId, agentName, traceId, executionId, deliverableId, taskDescription, contextSnapshot, feedback, onFeedback, canRecordFeedback])

  const sizeClasses = {
    sm: 'w-6 h-6 p-1',
    md: 'w-8 h-8 p-1.5',
  }

  const iconSize = size === 'sm' ? 14 : 18

  // If no agent identifier, don't render (can't record feedback without knowing the agent)
  if (!canRecordFeedback) return null

  return (
    <div className={cn('inline-flex items-center gap-1', className)}>
      {/* Thumbs Up */}
      <button
        onClick={() => handleFeedback(1)}
        disabled={state !== 'idle' || feedback !== null}
        title={feedback === 'positive' ? 'Marked as helpful' : agentName ? `${agentName} was helpful` : 'Helpful'}
        className={cn(
          'rounded-md transition-colors',
          sizeClasses[size],
          feedback === 'positive'
            ? 'bg-green-500/20 text-green-400'
            : feedback === null && state === 'idle'
              ? 'hover:bg-muted text-muted-foreground hover:text-foreground'
              : 'text-muted-foreground/50 cursor-not-allowed',
        )}
      >
        {state === 'submitting' ? (
          <Loader2 size={iconSize} className="animate-spin" />
        ) : feedback === 'positive' ? (
          <Check size={iconSize} />
        ) : (
          <ThumbsUp size={iconSize} />
        )}
      </button>

      {/* Thumbs Down */}
      <button
        onClick={() => handleFeedback(-1)}
        disabled={state !== 'idle' || feedback !== null}
        title={feedback === 'negative' ? 'Marked as not helpful' : agentName ? `${agentName} was not helpful` : 'Not helpful'}
        className={cn(
          'rounded-md transition-colors',
          sizeClasses[size],
          feedback === 'negative'
            ? 'bg-red-500/20 text-red-400'
            : feedback === null && state === 'idle'
              ? 'hover:bg-muted text-muted-foreground hover:text-foreground'
              : 'text-muted-foreground/50 cursor-not-allowed',
        )}
      >
        {state === 'submitting' ? (
          <Loader2 size={iconSize} className="animate-spin" />
        ) : feedback === 'negative' ? (
          <Check size={iconSize} />
        ) : (
          <ThumbsDown size={iconSize} />
        )}
      </button>

      {/* Error indicator */}
      {error && (
        <span className="text-xs text-red-400 ml-1" title={error}>!</span>
      )}
    </div>
  )
}

export default FeedbackButtons
