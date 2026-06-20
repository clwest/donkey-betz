/**
 * Session 1175 PR-2b-3 — Agent-completion banner.
 *
 * The transient live signal half of the follow-up wake design. The chat
 * bubble (persisted ChatConversation row written by the PR-2b-2 consumer)
 * is the load-bearing record that survives a page refresh; this banner is
 * the "pay attention, something finished" pop-up that fires the moment the
 * WS `agent.completed` event lands, so the user notices even if they're
 * scrolled away from the bottom of the chat.
 *
 * Subscribes to `usePARecentAgentCompletion` from the PA store, which is
 * driven by the `agent.completed` WebSocket event handler in
 * CommandCenterPage. Mirrors the RigbyToolTicker (Session 1172) pattern:
 * non-intrusive, fade-out after a short window, click to dismiss early,
 * returns null when idle.
 */
import { useEffect, useState } from 'react'
import { CheckCircle2, AlertTriangle, X } from 'lucide-react'
import { usePARecentAgentCompletion, usePAStore } from '@/stores/paStore'

// The banner shows agent name + execution_id + status. A 6-second window
// is longer than RigbyToolTicker's 2.5s because the user needs time to
// read the agent name and decide whether to scroll to the new chat
// message. Manually dismissable.
const FADE_MS = 6000

export function AgentCompletionBanner() {
  const completion = usePARecentAgentCompletion()
  const clearAgentCompletion = usePAStore((s) => s.clearAgentCompletion)
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    if (completion) {
      setVisible(true)
      const t = setTimeout(() => {
        setVisible(false)
        clearAgentCompletion()
      }, FADE_MS)
      return () => clearTimeout(t)
    }
  }, [completion, clearAgentCompletion])

  if (!completion || !visible) return null

  const isError = completion.status === 'failed'
  const Icon = isError ? AlertTriangle : CheckCircle2
  const color = isError ? 'text-amber-500' : 'text-emerald-500'
  const verb = isError ? 'failed' : 'finished'

  const handleDismiss = () => {
    setVisible(false)
    clearAgentCompletion()
  }

  return (
    <div
      className="flex items-center gap-2 px-3 py-2 text-xs text-muted-foreground bg-muted/50 border-t border-border/40 transition-opacity duration-500"
      role="status"
      aria-live="polite"
    >
      <Icon className={`w-4 h-4 ${color} flex-shrink-0`} />
      <span className="flex-1 min-w-0 truncate">
        Agent <code className="font-mono text-foreground">{completion.agent_name || 'agent'}</code> {verb}
        {completion.error_signature && (
          <span className="opacity-70"> — {completion.error_signature}</span>
        )}
        <span className="opacity-50"> · see chat below</span>
      </span>
      <button
        type="button"
        onClick={handleDismiss}
        className="p-0.5 rounded hover:bg-muted/80 focus:outline-none focus:ring-1 focus:ring-border"
        aria-label="Dismiss agent completion notice"
      >
        <X className="w-3 h-3" />
      </button>
    </div>
  )
}
