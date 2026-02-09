/**
 * Session 971b: Page tracking hook for telemetry.
 * Tracks route, workspace tab, and subtab changes to Redis counters.
 * Never throws, never blocks UI.
 */

import { useEffect, useRef } from 'react'
import { useLocation } from 'react-router-dom'

const DEBOUNCE_MS = 500

/** Fire-and-forget POST — silently swallows errors. */
function sendPageView(route: string, tab?: string | null, subtab?: string | null) {
  const body: Record<string, string> = { route }
  if (tab) body.tab = tab
  if (subtab) body.subtab = subtab

  try {
    fetch('/api/v1/telemetry/page-view/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(body),
    }).catch(() => {}) // swallow network errors
  } catch {
    // swallow synchronous errors
  }
}

/**
 * Track route changes (App-level).
 * Call once in a top-level component.
 */
export function usePageTracking() {
  const location = useLocation()
  const timerRef = useRef<ReturnType<typeof setTimeout>>()

  useEffect(() => {
    clearTimeout(timerRef.current)
    timerRef.current = setTimeout(() => {
      const params = new URLSearchParams(location.search)
      sendPageView(location.pathname, params.get('tab'), params.get('subtab'))
    }, DEBOUNCE_MS)

    return () => clearTimeout(timerRef.current)
  }, [location.pathname, location.search])
}

/**
 * Track workspace tab/subtab changes explicitly.
 * Call from WorkspacePageNew when the active tab or subtab changes.
 */
export function useWorkspaceTabTracking(tab: string, subtab?: string) {
  const timerRef = useRef<ReturnType<typeof setTimeout>>()

  useEffect(() => {
    clearTimeout(timerRef.current)
    timerRef.current = setTimeout(() => {
      sendPageView('/workspace', tab, subtab)
    }, DEBOUNCE_MS)

    return () => clearTimeout(timerRef.current)
  }, [tab, subtab])
}
