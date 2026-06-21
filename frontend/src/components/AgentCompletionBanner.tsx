/**
 * Session 1175 PR-2b-3 — Agent-completion banner.
 *
 * The transient live signal half of the follow-up wake design. The chat
 * bubble (persisted ChatConversation row written server-side by the fire
 * helper post-PR #2352) is the load-bearing record that survives a page
 * refresh; this banner is the "pay attention, something finished" pop-up
 * that fires the moment the WS `agent.completed` event lands, so the user
 * notices even if they're scrolled away from the bottom of the chat.
 *
 * Session 1181 PR4 — banner queue: when two or more agents complete in
 * close succession (multi-agent fanout — Pass B Cell 7), each gets its
 * own toast in a vertical stack rather than the newer one silently
 * overwriting the older. Each toast carries its own 6s fade timer + an
 * X dismiss control. Order is newest-first; queue capped at 10 by the
 * store.
 */
import { useEffect, useState } from 'react'
import { CheckCircle2, AlertTriangle, X } from 'lucide-react'
import { usePAAgentCompletionQueue, usePAStore } from '@/stores/paStore'

// 6-second window: longer than RigbyToolTicker's 2.5s because the user
// needs time to read the agent name and decide whether to scroll to the
// new chat message. Manually dismissable.
const FADE_MS = 6000

interface AgentCompletion {
  execution_id: string
  agent_name: string
  status: string
  error_signature?: string | null
}

function CompletionToast({ completion }: { completion: AgentCompletion }) {
  const dismissAgentCompletion = usePAStore((s) => s.dismissAgentCompletion)
  const [visible, setVisible] = useState(true)

  useEffect(() => {
    const t = setTimeout(() => {
      setVisible(false)
      dismissAgentCompletion(completion.execution_id)
    }, FADE_MS)
    return () => clearTimeout(t)
  }, [completion.execution_id, dismissAgentCompletion])

  if (!visible) return null

  const isError = completion.status === 'failed'
  const Icon = isError ? AlertTriangle : CheckCircle2
  const color = isError ? 'text-amber-500' : 'text-emerald-500'
  const verb = isError ? 'failed' : 'finished'

  const handleDismiss = () => {
    setVisible(false)
    dismissAgentCompletion(completion.execution_id)
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

export function AgentCompletionBanner() {
  const queue = usePAAgentCompletionQueue()

  if (queue.length === 0) return null

  return (
    <div className="flex flex-col">
      {queue.map((completion) => (
        <CompletionToast key={completion.execution_id} completion={completion} />
      ))}
    </div>
  )
}
