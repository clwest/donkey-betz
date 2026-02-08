// Session 968: Dev-only debug footer showing API request log for a given scope
import { useState, useEffect, useMemo } from 'react'
import { ChevronDown, ChevronUp, Trash2 } from 'lucide-react'
import { subscribeRequestLog, clearRequestLog, type RequestLogEntry } from '@/lib/api'

const DEV_KEY = 'showDebugPanels'

function getDebugEnabled(): boolean {
  try {
    const stored = localStorage.getItem(DEV_KEY)
    if (stored !== null) return stored === 'true'
    return import.meta.env.DEV
  } catch {
    return false
  }
}

interface PanelDebugDrawerProps {
  scope: string
}

export function PanelDebugDrawer({ scope }: PanelDebugDrawerProps) {
  const [enabled] = useState(getDebugEnabled)
  const [open, setOpen] = useState(false)
  const [entries, setEntries] = useState<RequestLogEntry[]>([])

  useEffect(() => {
    if (!enabled) return
    return subscribeRequestLog(setEntries)
  }, [enabled])

  const scoped = useMemo(
    () => entries.filter((e) => e.scope === scope),
    [entries, scope]
  )

  if (!enabled) return null

  const last = scoped[scoped.length - 1]

  return (
    <div className="mt-4 border-t border-gray-800 pt-2 text-[11px] text-gray-500 font-mono select-none">
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-1 hover:text-gray-400 transition-colors w-full"
      >
        {open ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
        <span>
          {scope} — {scoped.length} request{scoped.length !== 1 ? 's' : ''}
          {last
            ? ` — last: ${last.method} ${last.url.replace(/^\/api/, '')} (${last.status ?? '…'}, ${last.ms}ms)`
            : ' — no requests fired (likely unwired)'}
        </span>
      </button>

      {open && (
        <div className="mt-2 max-h-48 overflow-y-auto space-y-0.5">
          {scoped.length === 0 && (
            <p className="text-gray-600 italic py-2">No requests fired by this view</p>
          )}
          {scoped.map((e) => (
            <div
              key={e.id}
              className="flex items-center gap-2 px-1 py-0.5 rounded hover:bg-gray-800/50"
            >
              <span className="w-8 text-right tabular-nums">{e.status ?? '…'}</span>
              <span
                className={
                  e.status && e.status < 400
                    ? 'text-green-600'
                    : e.status
                      ? 'text-red-500'
                      : 'text-gray-600'
                }
              >
                {e.method}
              </span>
              <span className="truncate flex-1">{e.url.replace(/^\/api/, '')}</span>
              <span className="text-gray-600 tabular-nums">{e.ms}ms</span>
              {e.error && <span className="text-red-600 truncate max-w-[120px]">{e.error}</span>}
            </div>
          ))}
          {scoped.length > 0 && (
            <button
              onClick={() => clearRequestLog()}
              className="flex items-center gap-1 text-gray-600 hover:text-gray-400 mt-1 px-1"
            >
              <Trash2 size={10} />
              Clear log
            </button>
          )}
        </div>
      )}
    </div>
  )
}
