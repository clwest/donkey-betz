/**
 * Session 1172 — Rigby tool-lifecycle ticker.
 *
 * Renders a thin strip showing the tool Rigby is currently calling
 * (with a spinner) or the last tool she just finished (with a check or
 * warning icon, depending on status). Auto-clears the "recent" state
 * after a short fade so the strip doesn't permanently take chat space.
 *
 * Subscribes to `usePAActiveTool` / `usePARecentTool` from the PA store,
 * which are themselves driven by `rigby.tool.started` /
 * `rigby.tool.completed` WebSocket events handled in CommandCenterPage.
 *
 * Event contract reference: docs/handoffs/SESSION_1172_*.md (1172-1 spec).
 */
import { useEffect, useState } from 'react'
import { Loader2, Check, AlertTriangle } from 'lucide-react'
import { usePAActiveTool, usePARecentTool, usePAStore } from '@/stores/paStore'

const RECENT_FADE_MS = 2500

export function RigbyToolTicker() {
  const activeTool = usePAActiveTool()
  const recentTool = usePARecentTool()
  const clearToolTicker = usePAStore((s) => s.clearToolTicker)

  // Render the recent completed tool for a brief window so the user
  // sees the latency + status before it disappears, then clear it.
  const [showRecent, setShowRecent] = useState(false)
  useEffect(() => {
    if (recentTool) {
      setShowRecent(true)
      const t = setTimeout(() => {
        setShowRecent(false)
        // Only clear the recent state if no new activeTool arrived since.
        if (!usePAStore.getState().activeTool) {
          clearToolTicker()
        }
      }, RECENT_FADE_MS)
      return () => clearTimeout(t)
    }
  }, [recentTool, clearToolTicker])

  if (activeTool) {
    return (
      <div
        className="flex items-center gap-2 px-3 py-1.5 text-xs text-muted-foreground bg-muted/40 border-t border-border/40"
        role="status"
        aria-live="polite"
      >
        <Loader2 className="w-3 h-3 animate-spin" />
        <span>
          Rigby is using <code className="font-mono text-foreground">{activeTool.tool_name}</code>...
        </span>
      </div>
    )
  }

  if (recentTool && showRecent) {
    const isError = recentTool.status === 'error'
    const Icon = isError ? AlertTriangle : Check
    const color = isError ? 'text-amber-500' : 'text-emerald-500'
    return (
      <div
        className="flex items-center gap-2 px-3 py-1.5 text-xs text-muted-foreground bg-muted/30 border-t border-border/40 transition-opacity duration-500"
        role="status"
        aria-live="polite"
      >
        <Icon className={`w-3 h-3 ${color}`} />
        <span>
          Rigby used <code className="font-mono text-foreground">{recentTool.tool_name}</code>
          {typeof recentTool.latency_ms === 'number' && (
            <span className="opacity-70"> · {recentTool.latency_ms}ms</span>
          )}
        </span>
      </div>
    )
  }

  return null
}
